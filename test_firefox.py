from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service

options = Options()
options.add_argument('--headless')
service = Service('/usr/local/bin/geckodriver')

driver = webdriver.Firefox(service=service, options=options)
driver.get("https://example.com")
print(driver.title)
driver.quit()
