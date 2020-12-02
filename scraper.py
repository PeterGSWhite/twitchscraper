from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
from db import create_connection, insert_category, insert_cat_occurrence

conn = create_connection('example.db')

url = 'https://www.twitch.tv/directory?sort=VIEWER_COUNT'

options = Options()
options.headless = True
driver = webdriver.Firefox(options=options)
driver.get(url)
driver.implicitly_wait(3)

categories = driver.find_elements_by_class_name('tw-card')

for cat in categories:
    title = cat.find_element_by_tag_name('h3').text
    viewers = cat.find_element_by_class_name('tw-c-text-alt-2').text
    href = cat.find_element_by_tag_name('a').get_attribute('href')
    insert_category(conn, href, title)
    insert_cat_occurrence(conn, href, viewers)
    
driver.save_screenshot('dir.png')
driver.close()