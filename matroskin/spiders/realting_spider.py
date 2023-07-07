import scrapy

from scrapy.utils.project import get_project_settings


settings = get_project_settings()


class RealtingSpider(scrapy.Spider):
    name = 'realting'
    start_urls = [settings.get('START_URL')]

    def parse(self, response):
        apartment_page_links = response.css('.gl > a::attr(href)').extract()
        yield from response.follow_all(apartment_page_links,
                                       self.parse_apartment)
        pagination_links = response.css('.dlf a')
        yield from response.follow_all(pagination_links, self.parse)

    def parse_apartment(self, response):
        def extract_with_css(query):
            return response.css(query).get(default='').strip()

        yield {
            'url': response.url,
            'summary': extract_with_css('h1::text'),
            'location': extract_with_css('.loc > a::attr(onclick)').split("'")[1],
            'price': extract_with_css('.price > span::text'),
            'about': dict(zip(response.css('.t::text').getall(),
                              response.css('.i::text').getall())),
        }
