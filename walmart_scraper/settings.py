# Scrapy settings for walmart_scraper project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html
from shutil import which
SELENIUM_DRIVER_NAME = 'chrome'
SELENIUM_DRIVER_EXECUTABLE_PATH = which('chromedriver')
SELENIUM_DRIVER_ARGUMENTS=['-headless','start-maximized','--disable-blink-features=AutomationControlled','--disable-blink-features']  # '--headless' if using chrome instead of firefox


BOT_NAME = 'walmart_scraper'

SPIDER_MODULES = ['walmart_scraper.spiders']
NEWSPIDER_MODULE = 'walmart_scraper.spiders'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

SCRAPEOPS_API_KEY = 'YOUR API KEY'

SCRAPEOPS_PROXY_ENABLED = False


#ITEM_PIPELINES = {
#   'walmart_scrapper.pipelines.WalmartScraperPipeline': 300,   
#}

# Add In The ScrapeOps Monitoring Extension
EXTENSIONS = {
'scrapeops_scrapy.extension.ScrapeOpsMonitor': 500, 
}


DOWNLOADER_MIDDLEWARES = {

    ## ScrapeOps Monitor
    'scrapeops_scrapy.middleware.retry.RetryMiddleware': 550,
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
    #'scrapy_selenium.SeleniumMiddleware': 725,
    ## Proxy Middleware
    #'scrapeops_scrapy_proxy_sdk.scrapeops_scrapy_proxy_sdk.ScrapeOpsScrapyProxySdk': 725,
}

# Max Concurrency On ScrapeOps Proxy Free Plan is 1 thread
CONCURRENT_REQUESTS = 1
