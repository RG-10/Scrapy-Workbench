import scrapy
from scrapy.utils.response import open_in_browser


class FortCollinsChamberSpider(scrapy.Spider):
    name = 'FortCollinsChamber'
    start_urls = ['https://web.fortcollinschamber.com/allcategories']
    base_url = 'https://web.fortcollinschamber.com{}'
    custom_settings = {
        'FEED_URI': 'FortCollinsChamber_Data.xlsx',
        'FEED_FORMAT': 'xlsx',
        'FEED_EXPORT_ENCODING': 'utf-8',
        'FEED_EXPORTERS': {'xlsx': 'scrapy_xlsx.XlsxItemExporter'},
        'FEED_EXPORT_FIELDS': [
        'Company Name', 'Company_Logo_url', 'Address_Street', 'Address_city', 'Address_state',
        'Address_zipcode', 'Contact', 'Member_Name', 'Member_Since', 'Website_urls', 'Social_media_urls'],
    }

    def start_requests(self):
        yield scrapy.Request(url=self.start_urls[0], callback=self.parse)

    def parse(self, response):
        # category urls
        category_links = response.xpath('//li[@class="ListingCategories_AllCategories_CATEGORY"]/a/@href').getall()
        for category_link in category_links:
            print(response.urljoin(category_link))
            yield scrapy.Request(url=response.urljoin(category_link), callback=self.parse_list_page)

    def parse_list_page(self, response):
        for url in response.css('div.ListingResults_All_CONTAINER'):
            #print(url.css('span[itemprop="name"] a::text').get())
            #item = dict()
            #item['Company Name'] =
            #yield item
            url = response.xpath('//div[@class="ListingResults_Level5_LOGO"]/a/@href').get()
            url = self.base_url.format(url)
            yield {
                'Company Name': response.xpath('//span[@itemprop="name"]/a/text()').get(),
                'Company_Logo_url': url,
                'Address_Street': response.xpath('//span[@itemprop="street-address"]/text()').get(),
                'Address_city': response.xpath('//span[@itemprop="locality"]/text()').get(),
                'Address_state': response.xpath('//span[@itemprop="region"]/text()').get(),
                'Address_zipcode': response.xpath('//span[@itemprop="postal-code"]/text()').get('').strip(),
                'Contact': response.xpath('//div[@class="ListingResults_Level5_PHONE1"]/text()').get(),
                'Member_Since': response.xpath('//div[@class="ListingResults_Level5_MEMBERSINCE"]/text()').get(),
                'Website_urls': response.xpath('//span[@class="ListingResults_Level5_VISITSITE"]/a/@href').get(),
                'Social_media_urls': ' | '.join(social.xpath('./@href').get() for social in
                                                 response.xpath('//div[@class="ListingResults_Level5_SOCIALMEDIA"]/a')),
            }


