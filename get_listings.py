#Tämä ohjelma hakee kaikkien myynnissä Oulun Heinäpäässä olevien kerrostaloasuntojen tiedot
#Ja tallentaa ne päivämäärä_listings.csv nimettyyn tiedostoon.
#Se avataan käsittelyä varten soup_testing.py tiedostossa
import os
from selenium import webdriver
#from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
#from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options as firefox_options
import time
import pandas as pd
import time
import random
from datetime import datetime

def current_date():
    return datetime.now().strftime('%d%m%Y')

start_time_etuovi = time.time()

if os.name == 'nt': #Windows
    geckodriver_path = 'geckodriver.exe'
else:
    geckodriver_path = '/usr/local/bin/geckodriver'

#New code for geckodriver
firefox_options = firefox_options()
firefox_options.add_argument("-headless")

#firefox_options.headless = True

if not os.path.exists(geckodriver_path):
    raise FileExistsError(f"Geckodriver not found at {geckodriver_path}")

driver = webdriver.Firefox(service = Service(geckodriver_path),options = firefox_options)

def wait_random():
    wait_time = random.uniform(1, 3)
    print(f"Waiting for {wait_time:.2f} seconds")
    time.sleep(wait_time)

def get_urls(base_url, page):

    try:
        spotlight = driver.find_element(By.ID, "spotlight-container-id")
        driver.execute_script("arguments[0].remove();", spotlight)
        print("Spotlight-mainos poistettu.")
    except:
        print("Ei spotlight-mainosta tällä sivulla.")


    print(base_url)
    driver.get(base_url)
    driver.implicitly_wait(10)

    # #Jos tulee cookies-popup
    try:
        accept_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "almacmp-modalConfirmBtn"))
        )
        accept_button.click()
    except Exception as e:
        print("Cookies-popup error")
        print(f"An error occurred: {e}")

    #Accessing <a hrefs>
    while True:
        full_url = f"{base_url}&sivu={page}"
        print(f"\nKäsitellään sivu {page}: {full_url}")
        driver.get(full_url)

        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        except Exception as e:
            print(f"Sivun latauksessa virhe: {e}")
            break

        wait_random()
        try:
            spotlight = driver.find_element(By.ID, "spotlight-container-id")
            driver.execute_script("arguments[0].remove();", spotlight)
            print("Spotlight-mainos poistettu.")
        except:
            print("Ei spotlight-mainosta tällä sivulla.")
        a_tags = driver.find_elements(By.TAG_NAME, 'a')
        filtered_hrefs = [a.get_attribute('href') for a in a_tags
                        if a.get_attribute('href') and "kohde" in a.get_attribute('href')]

        # Poistetaan parametrit URLin lopusta ja suodatetaan duplikaatit
        new_hrefs = []
        for href in filtered_hrefs:
            clean_href = href.split('?')[0]
            if clean_href not in seen_hrefs:
                seen_hrefs.add(clean_href)
                new_hrefs.append(clean_href)

        print(f"Löytyi {len(new_hrefs)} uutta linkkiä")

        if not new_hrefs:
            print("Ei uusia linkkejä – lopetetaan.")
            break

        url_list.extend(new_hrefs)
        page += 1

    driver.quit()

    date = current_date()
    #filename = f"{date}_listings.csv"

    df = pd.DataFrame(url_list, columns=['url'])
    df['fetch_date'] = current_date()
    df = df.drop_duplicates(subset = ['url'])


    print(f"Writing {len(url_list)} rows to csv")
    df.to_csv("latest_listings.csv", index=False)
    print("Save complete!")

    end_time_etuovi = time.time()
    execution_time_etuovi = end_time_etuovi - start_time_etuovi
    print(f"Execution time: {execution_time_etuovi:.2f} seconds")




if __name__ == "__main__":
    base_url = 'https://www.etuovi.com/myytavat-asunnot/oulu/heinapaa?haku=M2284191086'
    page = 1
    seen_hrefs = set()
    url_list = []
    get_urls(base_url, page)
    
