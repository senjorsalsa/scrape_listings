from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
import re

REGEX = r'^\$[\d,]+'
FORM_LINK = "https://docs.google.com/forms/d/e/1FAIpQLSexOUrOdrp1igZ1gMsLm8hwvPvfgKqkKqxFMyxrX6sK-itWlQ/viewform?usp=sf_link"
SCRAPE_LINK = "https://appbrewery.github.io/Zillow-Clone/"

# Fetching the scrape target and souping it
response = requests.get(SCRAPE_LINK)
soup = BeautifulSoup(response.text, "html.parser")

all_addresses = soup.find_all("address")
address_list = [address.get_text().strip().replace('|', '') for address in all_addresses]

all_prices = soup.find_all(class_='PropertyCardWrapper__StyledPriceLine')

price_list = [re.match(REGEX, price.text).group() for price in all_prices]

all_links = soup.find_all(class_="property-card-link")
links_list = [link['href'] for link in all_links]

# Open Chrome with Selenium and prepare to submit to form
chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach", True)
driver = webdriver.Chrome(options=chrome_options)

driver.get(FORM_LINK)
driver.implicitly_wait(4)

# Submitting all listings to the form one by one
for i in range(len(address_list)):
    address_input = driver.find_element(By.XPATH, value='//*[@id="mG61Hd"]/div[2]/div/div[2]/div[1]/div/div/div[2]/div/div[1]/div/div[1]/input')
    address_input.click()
    address_input.send_keys(address_list[i])

    price_input = driver.find_element(By.XPATH, value='//*[@id="mG61Hd"]/div[2]/div/div[2]/div[2]/div/div/div[2]/div/div[1]/div/div[1]/input')
    price_input.click()
    price_input.send_keys(price_list[i])

    link_input = driver.find_element(By.XPATH, value='//*[@id="mG61Hd"]/div[2]/div/div[2]/div[3]/div/div/div[2]/div/div[1]/div/div[1]/input')
    link_input.click()
    link_input.send_keys(links_list[i])

    submit_button = driver.find_element(By.XPATH, value='//*[@id="mG61Hd"]/div[2]/div/div[3]/div[1]/div[1]/div/span/span')
    submit_button.click()

    driver.implicitly_wait(2)

    new_reply = driver.find_element(By.XPATH, value='/html/body/div[1]/div[2]/div[1]/div/div[4]/a')
    new_reply.click()

    print(f"Submitted {i + 1}/{len(address_list)}")

    driver.implicitly_wait(2)

# Exit Chrome, closing all open tabs
driver.quit()
