import time
import csv
from datetime import datetime, timedelta
from scraper_file.base_scraper import BaseScraper
from utils.selenium_utils import wait_for_element
from selenium.webdriver.common.by import By

class PrivateEquityScraper(BaseScraper):
    def __init__(self, headless=True):
        super().__init__(headless)
        self.website = "https://www.dealstreetasia.com/section/private-equity"
        self.csv_filename = "private_equity_articles.csv"
        self.two_months_ago = datetime.now() - timedelta(days=60)  # Ignore articles older than 2 months

    def parse_and_format_date(self, date_str):
        """Convert '14 January, 2025' into '14 ,01, 2025'."""
        try:
            parsed_date = datetime.strptime(date_str, "%d %B, %Y")
            return parsed_date.strftime("%d ,%m, %Y")
        except ValueError:
            return None  # Handle unexpected formats

    def scrape_articles(self):
        """Scrape articles from Private Equity section of DealStreetAsia."""
        self.open_page(self.website)

        with open(self.csv_filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["Title", "Source", "Date", "Article Content", "URL"])  # CSV Header

            last_article_old = False
            last_scraped_index = 0 

            while not last_article_old:
                articles = self.driver.find_elements(By.XPATH, '//*[@id="archive-wrapper"]/div[4]/div[1]/div/div')
                article_links = [article.find_element(By.XPATH, './div[1]/a').get_attribute('href') for article in articles]

                for i in range(last_scraped_index, len(article_links)):
                    link = article_links[i]
                    self.driver.get(link)
                    time.sleep(2)

                    try:
                        title = wait_for_element(self.driver, '//*[@id="disable-copy"]/h1').text.strip()
                        source = wait_for_element(self.driver, '//*[@id="disable-copy"]/div[2]/div[1]/div/div[1]/span/a').text.strip()
                        date_text = wait_for_element(self.driver, '//*[@id="disable-copy"]/div[2]/div[1]/div/div[1]/p').text.strip()
                        body = wait_for_element(self.driver, '//*[@id="disable-copy"]/div[2]/div[2]/div[1]/article').text.strip().replace("\n", " ")

                        formatted_date = self.parse_and_format_date(date_text)
                        article_date = datetime.strptime(formatted_date, "%d ,%m, %Y") if formatted_date else None

                        if article_date and article_date < self.two_months_ago:
                            print(f" Stopping: Found an article older than 2 months ({formatted_date})")
                            last_article_old = True
                            break

                        writer.writerow([title, source, formatted_date, body, link])
                        print(f" Saved: {title} - {formatted_date}")
                    except Exception as e:
                        print(f" Error extracting article data from {link}: {e}")

                    last_scraped_index = i + 1
                    self.driver.back()
                    time.sleep(2)

                if last_article_old:
                    break

                try:
                    more_button = self.driver.find_element(By.XPATH, '//*[@id="archive-wrapper"]/div[5]/div/button')
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", more_button)
                    time.sleep(1)
                    self.driver.execute_script("arguments[0].click();", more_button)
                    time.sleep(5)

                    last_scraped_index = len(article_links)
                except:
                    print("No 'More' button found or can't be clicked. Stopping.")
                    break

        print(f"\n Scraping complete! Data saved to {self.csv_filename}")
        self.close()
