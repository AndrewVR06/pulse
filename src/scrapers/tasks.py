from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapers.spiders.crypto_panic import CryptoPanic
from celery_app import celery_app


@celery_app.task()
def crawl_crypto_panic():
    process = CrawlerProcess(get_project_settings())
    process.crawl(CryptoPanic)
    process.start()
