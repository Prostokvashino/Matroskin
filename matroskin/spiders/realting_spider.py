import scrapy

from scrapy.utils.project import get_project_settings


settings = get_project_settings()


class RealtingSpider(scrapy.Spider):
    name = 'realting'
    start_urls = [settings.get('START_URL')]

    def parse(self, response):
        links = response.css('.gl > a::attr(href)').extract()
        for link in links:
            scraped_info = {
                'id': link.split("/")[-1],
            }
            yield scraped_info
