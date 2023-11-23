import scrapy


class CSBNConnectSpider(scrapy.Spider):
    name = 'CSBNConnect'
    start_urls = ['https://www.csbnconnect.com/categories']
    base_url = 'https://www.csbnconnect.com{}'
    custom_settings = {
        'FEED_URI': 'output/CSBNConnect_Data.csv',
        'FEED_FORMAT': 'csv',
        'FEED_EXPORT_ENCODING': 'utf-8',
        'ITEM_PIPELINES': {'CSBNConnect.pipelines.CSBNConnectImagesPipeline': 1},
        'IMAGES_STORE': 'images',
        'DOWNLOAD_DELAY': 1
    }

    def start_requests(self):
        yield scrapy.Request(url=self.start_urls[0], callback=self.parse)

    def parse(self, response):
        category_links = response.xpath('//div[@class="col-md-3  col-xs-6"]/a/@href').getall()
        for category_link in category_links:
            yield scrapy.Request(url=response.urljoin(category_link), callback=self.parse_list_page)

    def parse_list_page(self, response):
        for url in response.xpath('//div[@class="col-xs-12 nopad"]/a'):
            detail_url = url.xpath('./@href').get()
            yield scrapy.Request(url=response.urljoin(detail_url), callback=self.parse_detail_page)

        # pagination
        for href in response.xpath('//link[@rel="next" or @rel="prev"]/@href').getall():
            yield response.follow(href, callback=self.parse_list_page)

    def parse_detail_page(self, response):
        yield {'Name': response.xpath('//div[contains(@class,"nohpad")]/h2/text()').get().strip(),
               'Category': response.xpath('//span[contains(@class,"primary_color_page")]/text()').get().strip(),
               'BIO': ' '.join(response.xpath('//div[@dir="auto"]/text()').getall()).strip(), 'Services': ' '.join(
                service.strip() for service in response.xpath('//div[@class="col-md-12"]/text()').getall()),
               'Social_Media': ' | '.join(
                   social.xpath('./@href').get() for social in response.xpath('//div[@class="col-md-12 nohpad"]/a')),
               'Ratings': response.xpath('//span[@class="small inline-block"]/text()').get(),
               'Year Established': response.xpath('//div[@class="col-md-8"]/text()').get(default='').strip(),
               'Hours_of_Operations': response.xpath('(//div[@class="col-md-8"]/text())[2]').get().strip(),
               'Payment Methods': response.xpath('(//div[@class="col-md-8"]/text())[3]').get().strip(),
               'Credentials': response.xpath('(//div[@class="col-md-8"]/text())[4]').get().strip(),
               'Company Name': response.xpath('//div[@class="col-md-8"]/text()').get().strip(),
               'Company Website': response.xpath('(//div[@class="col-md-8"]/a/@href)[1]').get().strip(),
               'Online_Social_Urls': ' | '.join(
                   social.xpath('./@href')[0].get() for social in response.xpath('//div[@class="col-md-8"]/a')),
               'Phone': response.xpath('(//div[@class="col-md-8"]/a/@href)[5]').get(),
               'Location': response.xpath('//span[@class="location_text"]/div/p/text()').get().strip(),
               'Images': response.urljoin(response.xpath('//img[@class="profile_photo"]/@src').get())}
        item = dict()
        item['Images'] = response.urljoin(response.xpath('//img[@class="profile_photo"]/@src').get())
