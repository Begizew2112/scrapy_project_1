import scrapy
import time
import scrapy
from scrapy.http import HtmlResponse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager

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

        click_count = 0  # Track how many times the button is clicked
        max_clicks = 5   # Limit to 5 clicks

        while click_count < max_clicks:
            time.sleep(2)  # Wait for articles to load
            try:
                more_button = self.driver.find_element(By.XPATH, '//*[@id="archive-wrapper"]/div[5]/div/button')
                self.driver.execute_script("arguments[0].scrollIntoView();", more_button)
                time.sleep(1)
                more_button.click()
                time.sleep(3)  # Wait for new articles to load
                click_count += 1  # Increment click count
                print(f"'More' button clicked {click_count} times.")
            except:
                print("No 'More' button found. Stopping.")
                break  # Stop if the button is not found

        # Get the fully loaded page source
        html = self.driver.page_source
        self.driver.quit()

        # Convert Selenium HTML to Scrapy response
        sel_response = HtmlResponse(url=response.url, body=html, encoding='utf-8')

        # Extract all articles
        allnews = sel_response.css("div.main-list-row")
        for news in allnews:
            yield {          
                'source': news.css("p.category-link a::text").get(),
                'url': news.css("a::attr(href)").get(),
                'title': news.css("a h3::text").get(),
                'body': news.css("div.excerpt p::text").get(),
            }