import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import SberbankczItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class SberbankczSpider(scrapy.Spider):
	name = 'sberbankcz'
	start_urls = ['https://www.sberbank.cz/cs-cz/novinky']

	def parse(self, response):
		post_links = response.xpath('//h3/a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		next_page = response.xpath('//p[@class="u-pt-md"]/a/@href').get()
		if next_page:
			yield response.follow(next_page, self.parse)


	def parse_post(self, response):
		date = response.xpath('//p[@class="u-font-sm u-color-grey"]/text()').get().strip()
		title = response.xpath('//h1[@class="h2"]/text()').get()
		content = response.xpath('//div[@class="b-msg-detail u-mb-lg"]//text()[not (ancestor::h1 or ancestor::p[@class="u-font-sm u-color-grey"] or ancestor::div[@class="b-column-list u-mb-lg"])]').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=SberbankczItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
