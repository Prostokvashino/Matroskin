import re

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

        result = {
            'url': response.url,
            'summary': extract_with_css('h1::text'),
            'location': extract_with_css('.loc > a::attr(onclick)').split("'")[1],
            'price': extract_with_css('.price > span::text')
        }

        result.update(dict(zip(response.css('.t::text').getall(),
                               response.css('.i::text').getall())))

        map_link = extract_with_css('.loc > a::attr(onclick)').split("'")[3]

        yield response.follow(map_link,
                              self.parse_coordinates,
                              meta={'result': result})

    def parse_coordinates(self, response):
        def extract_with_css(query):
            return response.css(query).get(default='').strip()

        coordinates = re.search(r"\[([\d.,]+)\]",
                                extract_with_css('script::text')).group(1)

        coordinates_list = [float(coord) for coord in coordinates.split(",")]

        result = response.meta['result']

        result['latitude'] = coordinates_list[0]
        result['longitude'] = coordinates_list[1]

        yield result
