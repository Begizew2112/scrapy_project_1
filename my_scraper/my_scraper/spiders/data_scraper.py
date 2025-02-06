
# class dealprivatespiderSpider(scrapy.Spider):
#     name = 'newsspider'
#     allowed_domains = ['dealstreetasia.com/section/private-equit']
#     start_urls = ['https://www.dealstreetasia.com/section/private-equity']
#     def __init__(self):
#         options = Options()
#         options.add_argument("--headless")  # Run in headless mode
#         options.add_argument("--disable-blink-features=AutomationControlled")
#         self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


#     def parse(self, response):
#         self.driver.get(response.url)
#         allnews =response.css("div.main-list-row")
#         for news in allnews:
#             yield {          
#                 'source':news.css("p.category-link a::text").get(),
#                 'url' : news.css("a").attrib['href'],
#                 'title' :news.css("a h3::text").get(),
#                 'body': news.css("div.excerpt p::text").get(),
#             } 

#         try:
#             more_button = self.driver.find_element(By.XPATH, '//*[@id="archive-wrapper"]/div[5]/div/button')
#             self.driver.execute_script("arguments[0].scrollIntoView(true);", more_button)
#             time.sleep(1)
#             self.driver.execute_script("arguments[0].click();", more_button)
#             time.sleep(5)
#         except:
#             print("No 'More' button found or can't be clicked. Stopping.")
import scrapy
import time
import datetime
from scrapy.http import HtmlResponse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


class DealPrivateSpider(scrapy.Spider):
    name = 'newsspider'
    allowed_domains = ['dealstreetasia.com']
    start_urls = ['https://www.dealstreetasia.com/section/private-equity']

    def __init__(self):
        options = Options()
        options.add_argument("--headless")  # Run in headless mode
        options.add_argument("--disable-blink-features=AutomationControlled")
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    def parse(self, response):
        self.driver.get(response.url)

        max_clicks = 10  # Max clicks to load more articles
        click_count = 0  

        while click_count < max_clicks:
            time.sleep(2)  
            try:
                more_button = self.driver.find_element(By.XPATH, '//*[@id="archive-wrapper"]/div[5]/div/button')
                self.driver.execute_script("arguments[0].scrollIntoView();", more_button)
                time.sleep(1)
                more_button.click()
                time.sleep(3)  
                click_count += 1  
                print(f"'More' button clicked {click_count} times.")
            except:
                print("No 'More' button found. Stopping.")
                break  

        html = self.driver.page_source
        self.driver.quit()

        sel_response = HtmlResponse(url=response.url, body=html, encoding='utf-8')

        allnews = sel_response.css("div.main-list-row")
        for news in allnews:
            article_url = news.css("a::attr(href)").get()
            if article_url:
                yield response.follow(article_url, self.parse_article)

    def parse_article(self, response):
        date_text = response.css('div.publish-date::text').get()
        formatted_date = self.parse_and_format_date(date_text)

        yield {
            'title': response.css("h1::text").get(),
            'source': response.css("div.author-name a::text").get(),
            'date': formatted_date,
            'body': " ".join(response.css("article p::text").getall()),
            'url': response.url
        }

    def parse_and_format_date(self, date_text):
        """ Convert date format to standard format (dd, mm, yyyy) """
        if date_text:
            try:
                date_obj = datetime.datetime.strptime(date_text, "%B %d, %Y")  # Example: "January 15, 2024"
                return date_obj.strftime("%d, %m, %Y")
            except ValueError:
                return None  # Return None if date parsing fails
        return None
