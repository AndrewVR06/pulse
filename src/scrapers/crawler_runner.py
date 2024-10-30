from pathlib import Path

from fastapi import HTTPException
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import logging
import subprocess
import sys
from scrapers.spiders.crypto_panic import CryptoPanic


class CrawlerRunner:
    def __init__(self):
        self.settings = get_project_settings()
        self.process = CrawlerProcess(self.settings)
        self.crawling = False
        # Get the absolute path to the src directory
        self.src_path = Path(__file__).parent

    def _run_spider(self):
        self.crawling = True
        self.process.crawl(CryptoPanic)
        self.process.start()
        self.crawling = False

    async def run_spider(self):
        try:
            if self.crawling:
                raise HTTPException(status_code=400, detail="A spider is already running")

            # Run scrapy command directly
            process = subprocess.Popen(
                ["scrapy", "crawl", "crypto_panic"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
                cwd=self.src_path,
            )

            # Print output in real-time
            while True:
                output = process.stdout.readline()
                if output:
                    print(output.strip())
                    sys.stdout.flush()

                error = process.stderr.readline()
                if error:
                    print(error.strip(), file=sys.stderr)
                    sys.stderr.flush()

                # Check if process has completed
                if process.poll() is not None:
                    break

            return_code = process.poll()
            if return_code != 0:
                raise Exception(f"Spider failed with return code {return_code}")

            return {"status": "success", "message": "Crawl completed successfully"}

        except Exception as e:
            self.crawling = False
            logging.error(f"Crawl failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Crawl failed: {str(e)}")
        finally:
            self.crawling = False
