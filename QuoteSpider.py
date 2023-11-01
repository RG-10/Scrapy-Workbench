import scrapy
from scrapy.http import FormRequest
from scrapy_splash import SplashRequest
from ..items import QuotescraperItem

class QuoteSpider(scrapy.Spider):
    name = 'quotespider'
    start_urls = ['https://quotes.toscrape.com/login']
    login_url = 'https://quotes.toscrape.com/login'
    url = 'https://quotes.toscrape.com/'
    scroll_url = "https://quotes.toscrape.com/scroll"

    custom_settings = {
        'FEED_URI': 'data.csv',
        'FEED_FORMAT': 'csv',
        'FEED_EXPORT_ENCODING': 'utf-8',
    }

    def parse(self, response):
        # Extracting the CSRF token
        csrf_token = response.css('input[name="csrf_token"]::attr(value)').get()

        # my login credentials
        username = 'admin'
        password = 'admin'

        # Form data to be sent in the POST request for login
        data = {
            'csrf_token': csrf_token,
            'username': username,
            'password': password,
        }

        # Send a POST request to the login URL with the form data
        yield FormRequest(self.login_url, formdata=data, callback=self.after_login)

    def after_login(self, response):
        # Check if login was successful
        if "Welcome" in response.text:
            self.logger.info("Login successful")
            # If the login is successful, proceed to the target page for scraping
            yield SplashRequest(url=self.scroll_url, callback=self.parse_quotes, args={'wait':2})
        else:
            self.logger.error("Login failed, try again")

    def parse_quotes(self, response):
        for quote in response.css('div.quote'):
            item = QuotescraperItem()
            item['title'] = quote.css('span.text::text').get('').replace('â€œ', '').strip()
            item['author'] = quote.css('.author::text').get()
            item['tag'] = ', '.join(quote.css('.tag::text').getall())
            yield item

        # Implementing scrolling by executing Js (scrolling down the page)
        script = "window.scrollTo(0, document.body.scrollHeight);"
        yield SplashRequest(url=response.url,callback=self.parse_quotes, args={'wait':10, 'lua_source':script})
