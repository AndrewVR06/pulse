from typing import Iterable
from urllib.parse import urlparse
from fake_useragent import UserAgent
import scrapy
from scrapy import Request
from scrapy.http import TextResponse
from scrapy_playwright.page import PageMethod

from app_config import get_settings
from scrapers.schemas.crypto_panic_api_schema import CryptoPanicApiResponse
from scrapers.schemas.database_pipeline_input_schema import DatabasePipelineInputSchema


def should_abort_request(request):
    parsed_url = urlparse(request.url)
    domain = parsed_url.netloc

    if domain in {"connect.facebook.net", "platform.twitter.com", "syndication.twitter.com", "fonts.googleapis.com"}:
        return True

    return (
        request.resource_type in ["image", "stylesheet", "media", "font"]
        or ".jpg" in request.url
        or ".png" in request.url
        or ".svg" in request.url
    )


class CryptoPanic(scrapy.Spider):
    name = "crypto_panic"
    custom_settings = {
        "PLAYWRIGHT_ABORT_REQUEST": should_abort_request,
        "PLAYWRIGHT_LAUNCH_OPTIONS": {"headless": True, "timeout": 20 * 1000},
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
        "DOWNLOAD_HANDLERS": {
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        },
        "ITEM_PIPELINES": {
            "scrapers.pipelines.database_pipeline.DatabasePipeline": 300,
            "scrapers.pipelines.extract_article_pipeline.ExtractArticlePipeline": 305,
            "scrapers.pipelines.summarise_article_pipeline.SummariseArticlePipeline": 310,
            "scrapers.pipelines.index_article_pipeline.IndexArticlePipeline": 315,
        },
        "DOWNLOAD_DELAY": 1,
        "RANDOMIZE_DOWNLOAD_DELAY": True,
        "DOWNLOAD_TIMEOUT": 300,
    }

    def start_requests(self) -> Iterable[Request]:
        """
        Use the crypto panic API to get the list of URLs to visit. Each URL is a reference to a crypto panic site. We
        will need to navigate through there to get the sites of interest.
        """
        api = f"https://cryptopanic.com/api/v1/posts/?auth_token={get_settings().CRYPTO_PANIC_API_KEY}&public=true&kind=news&page=1"
        yield scrapy.Request(url=api, callback=self.parse_api_response)

    def parse_api_response(self, response: TextResponse) -> None:
        """
        Retrieve the API response from Crypto Panic and create Pydantic schemas
        :param response:
        :return:
        """
        parsed_response = CryptoPanicApiResponse.model_validate(response.json())

        yield from (
            scrapy.Request(
                str(rep.url),
                meta={
                    "playwright": True,
                    "playwright_page_methods": [
                        PageMethod("wait_for_selector", selector=".post-header", state="visible", timeout=5000),
                    ],
                    "cryptopanic_response": rep,
                },
                callback=self.parse_crypto_panic_url,
            )
            for rep in parsed_response.results[:1]
        )

    def parse_crypto_panic_url(self, response: TextResponse) -> None:
        """
        Retrieve the URL of the external source from the Crypto Panic page
        :param response:
        :return:
        """
        cookies = response.headers.getlist("Set-Cookie")
        url = response.css("div.post-header h1.post-title a:not(.close-button)::attr(href)").get()
        yield scrapy.Request(
            url,
            headers={"User-Agent": UserAgent().random},
            cookies={cookie.split(b"=")[0].decode(): cookie.split(b"=")[1].decode() for cookie in cookies},
            meta={
                "playwright": True,
                "playwright_page_methods": [
                    PageMethod("wait_for_timeout", timeout=3000),
                ],
                "cryptopanic_response": response.meta["cryptopanic_response"],
            },
            callback=self.parse_3rd_party_url,
        )

    def parse_3rd_party_url(self, response: TextResponse) -> None:
        """
        Receive and handle the URL of the external source
        """
        paragraphs = response.css("p *::text").getall()
        content = " ".join(paragraphs)

        yield DatabasePipelineInputSchema(content=content, source_url=response.url, cryptopanic_response=response.meta["cryptopanic_response"])
