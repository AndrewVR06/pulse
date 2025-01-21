from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from celery_app import celery_app
from scrapers.spiders.crypto_panic import CryptoPanic


@celery_app.task()
def crawl_crypto_panic():
    process = CrawlerProcess(get_project_settings())
    process.crawl(CryptoPanic)
    process.start()
