import re

import scrapy


class RealtingSpider(scrapy.Spider):
    name = 'realting'

    def start_requests(self):
        return [
            scrapy.Request(
                self.settings.get('START_URL'),
                callback=self.parse,
            )
        ]

    def parse(self, response):
        apartment_page_links = response.css('.gl > a::attr(href)').extract()
        yield from response.follow_all(apartment_page_links,
                                       self.parse_apartment)
        pagination_link = response.css('.dlf > span + a::attr(href)').get()
        if pagination_link:
            yield response.follow(pagination_link, self.parse)

    def parse_apartment(self, response):
        def extract_with_css(query):
            return response.css(query).get(default='').strip()

        date_time = ''
        spans = response.css('.footer span::text')
        if len(spans) > 2:
            match = re.search(r"(\d{2}\.\d{2}\.\d{4} \d{2}:\d{2})",
                              spans[2].get())
            date_time = match.group(1)

        result = {
            'id': response.url.split('/')[-1],
            'url': response.url,
            'summary': extract_with_css('h1::text'),
            'location': extract_with_css('.loc > a::attr(onclick)').split("'")[1],
            'price': extract_with_css('.price > span::text'),
            'posted_at': extract_with_css('.footer span::attr(content)'),
            'updated_at': date_time,
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
