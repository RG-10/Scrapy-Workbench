import scrapy

class BooksSpider(scrapy.Spider):
    name = "bookspider"
    start_urls = ["https://books.toscrape.com/"]

    custom_settings = {
        'FEED_URI': 'BookData.csv',
        'FEED_FORMAT': 'csv',
        'FEED_EXPORT_ENCODING': 'utf-8',
    }
    base_url = "https://books.toscrape.com/{}"

    def parse(self, response):
         # Define the base URL
        for book in response.css("article.product_pod"):
            yield {
                'image_url': self.base_url.format(book.css("div.image_container img::attr(src)").get()),
                'star_rating': book.css("p.star-rating::attr(class)").get().split()[-1],
                'book_title': book.css("h3 a::attr(title)").get(),
                'in_stock': "In stock" in book.css("p.availability::text").get(),
                'book_detail_url': response.urljoin(book.css("h3 a::attr(href)").get())
            }

        next_page = response.css('li.next a ::attr(href)').get()
        if next_page is not None:
             if 'catalogue/' in next_page:
                 next_page_url = 'https://books.toscrape.com/' + next_page
             else:
                 next_page_url = 'https://books.toscrape.com/catalogue/' + next_page
             yield response.follow(next_page_url, callback=self.parse)
