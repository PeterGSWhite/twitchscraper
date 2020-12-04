from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
from collections import deque
from datetime import datetime
import re
from db import create_connection, insert_category, insert_cat_occurrence, insert_channel, insert_stream

# Misc helper objects
LANG = 'en'
lang_codes = {
    'en': '6ea6bca4-4712-4ab9-a906-e3336a9d8039'
}
def get_valid_filename(s):
    """Turn string into valid filename"""
    s = str(s).strip().replace(' ', '_')
    return re.sub(r'(?u)[^-\w.]', '', s)

# Setting up
conn = create_connection('example.db')
options = Options()
options.headless = True
driver = webdriver.Firefox(options=options)

# Scrape Directory page
url = 'https://www.twitch.tv/directory?sort=VIEWER_COUNT'
driver.get(url)
# If cookies button - click it
driver.implicitly_wait(3)
consent_banner = driver.find_element_by_class_name('consent-banner')
accept_button = consent_banner.find_element_by_xpath(".//button[@data-a-target='consent-banner-accept']")
accept_button.click()

categories = driver.find_elements_by_class_name('tw-card')
cats_q = deque() # want to scrape categories from left to right (so it looks nicer when taking screenshots), queue makes this efficient
for cat in categories:
    #title = cat.find_element_by_tag_name('h3').text
    body = cat.find_element_by_class_name('tw-card-body')
    viewers = body.find_element_by_class_name('tw-c-text-alt-2').text
    a_tag = body.find_element_by_tag_name('a')
    href = a_tag.get_attribute('href')
    title = a_tag.find_element_by_tag_name('h3').get_attribute('title')

    # Add to DB
    insert_category(conn, href, title)
    insert_cat_occurrence(conn, href, viewers)

    # Append to queue of categories for the next stage
    print(title,href)
    cats_q.append((title, href))

print('Saving screenshot of Directory page')
ts = datetime.now().strftime("%m-%dT%H%M%S")
driver.save_screenshot(f'dir_page_{ts}.png')

# Set language tag
driver.execute_script("localStorage.setItem(arguments[0],arguments[1])", 'languageTags', f'["{lang_codes[LANG]}"]')

i = 0
# Scrape Category pages
while cats_q and i < 2:
    title, cat_href = cats_q.popleft()
    url = f'{cat_href}?sort=VIEWER_COUNT'
    print('Scraping', title, url)
    driver.get(url)
    driver.implicitly_wait(3)

    streams = driver.find_elements_by_tag_name('article')
    for stream in streams:
        viewers = stream.find_element_by_class_name('tw-media-card-stat').text
        channel_link = stream.find_element_by_xpath(".//a[@data-a-target='preview-card-channel-link']")
        channel_href = channel_link.get_attribute('href')
        channel_name = channel_link.text
        print(viewers, channel_name, channel_href)

        # Add to DB
        insert_channel(conn, channel_href, channel_name)
        insert_stream(conn, channel_href, cat_href, viewers)
    
    print(f'Saving screenshot of {title} page')
    ts = datetime.now().strftime("%m-%dT%H%M%S")
    driver.save_screenshot(f'{get_valid_filename(title)}_page_{ts}.png')
    i += 1

# Shutting down
driver.close()