import scrapy
import csv

class BookDetailSpider(scrapy.Spider):
    name = "BookDetailSpider"
    base_image_url = "https://books.toscrape.com/"

    custom_settings = {
        'FEED_URI': 'BookDetails.csv',
        'FEED_FORMAT': 'csv',
        'FEED_EXPORT_ENCODING': 'utf-8',
    }

    def start_requests(self):
        # Read the "BookData.csv" file and extract detail page URLs
        with open('BookData.csv', 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                detail_url = row['book_detail_url']
                yield scrapy.Request(detail_url, callback=self.parse)

    def parse(self, response):
        categories = response.css("ul.breadcrumb li:not(:first-child) a::text").getall()
        image_url = self.base_image_url + response.css("div.item.active img::attr(src)").get()
        title = response.css("h1::text").get()
        price = response.css("p.price_color::text").get()

        # Check for "In stock" condition
        in_stock = "In stock" in response.css("p.availability ::text").get().strip()
        # Check for "star rating" condition
        star_rating = response.css("p.star-rating::attr(class)").get().split()[-1]
        # Check for "warnings" condition
        warning = response.css("div.alert.alert-warning::text").get()
        # Check for "product description" condition
        product_description = response.css("meta[name='description']::attr(content)").get()

        # Extract product information in a table (if available)
        product_info = {}
        for row in response.css("table.table.table-striped tr"):
            key = row.css("th::text").get()
            value = row.css("td::text").get()
            if key and value:
                product_info[key.strip()] = value.strip()

        yield {
            'detail_page_url': response.url,
            'categories': ', '.join(categories),
            'image_url': image_url,
            'title': title,
            'price': price,
            'in_stock': in_stock,
            'stars': star_rating,
            'warning': warning,
            'product_description': product_description,
            'product_information': product_info,
        }

