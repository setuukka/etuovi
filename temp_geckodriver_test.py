from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile

geckodriver_path = "/usr/local/bin/geckodriver"
service = Service(geckodriver_path)

profile = FirefoxProfile()  # tyhjä profiili
options = Options()
options.profile = profile
options.headless = True  # halutessasi headless-tila

driver = webdriver.Firefox(service=service, options=options)

driver.get("https://www.google.com")
print(driver.title)
driver.quit()