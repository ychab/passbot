# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class EmailHistoryItem(scrapy.Item):
    spider = scrapy.Field()
    place = scrapy.Field()
    zipcode = scrapy.Field()
    date_slot = scrapy.Field()
    link = scrapy.Field()
    extra_data = scrapy.Field()
