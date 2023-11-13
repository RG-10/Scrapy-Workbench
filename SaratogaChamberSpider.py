import scrapy

class SaratogaChamberSpider(scrapy.Spider):
    name = 'SaratogaChamber'
    start_urls = ['https://chamber.saratoga.org/list']

    custom_settings = {
        'FEED_URI': 'ChamberSaratoga_Data.csv',
        'FEED_FORMAT': 'csv',
        'FEED_EXPORT_ENCODING': 'utf-8',
    }

    def start_requests(self):
        yield scrapy.Request(url=self.start_urls[0])

    def parse(self, response):
        # alphabet urls
        alphabet_links = response.xpath('//div[@class="btn-group gz-alphanumeric-btn"]/a/@href').getall()
        for alphabet_link in alphabet_links:
            yield scrapy.Request(url=response.urljoin(alphabet_link), callback=self.parse_list_page)

    def parse_list_page(self, response):
        for url in response.xpath('//div[@class="card-header"]/a'):
            detail_url = url.xpath('./@href').get()
            yield scrapy.Request(url=response.urljoin(detail_url), callback=self.parse_detail_page)

    def parse_detail_page(self, response):
        yield {
            'Name': response.xpath('//span[@class="fl-heading-text"]/text()').get(),
            'Address_street': response.xpath('//span[@itemprop="streetAddress"]/text()').get(),
            'Address_city': response.xpath('//span[@itemprop="addressLocality"]/text()').get(),
            'Address_state': response.xpath('//span[@itemprop="addressRegion"]/text()').get(),
            'Address_zipcode': response.xpath('//span[@itemprop="postalCode"]/text()').get(),
            'Mobile_number': response.xpath('//span[@itemprop="telephone"]/text()').get(),
            'Social_media_urls': ' | '.join(social.xpath('./@href').get() for social in response.xpath('//li[@class="list-group-item gz-card-social"]/a')),
            'Driving_directions': response.xpath('//div[@class="gz-details-driving"]/p/text()').get(),
            'Agent_name': response.xpath('//div[@class="gz-member-repname"]/text()').get(),
            'Agent_phone': response.xpath('//span[@class="gz-rep-phone-num"]/text()').get(),
            'Agent_address_street': response.xpath('//span[@itemprop="streetAddress"]/text()').getall(),
            'Agent_address_city': response.xpath('//span[@class="gz-address-city"]/text()').get(),
            'Agent_address_state': response.xpath('//span[@itemprop="addressRegion"]/text()').get(),
            'Agent_address_zipcode': response.xpath('//span[@itemprop="postalCode"]/text()').get()
        }
