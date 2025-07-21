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
from bs4 import BeautifulSoup, NavigableString
import re
import requests
from pathlib import Path
import numpy as np

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
    wait_time = random.uniform(1, 5)
    print(f"Waiting for {wait_time:.2f} seconds")
    time.sleep(wait_time)

def update_listing_file(url_list, filename='all_listings.csv'):
    file_path = Path(filename)
    if file_path.exists():
        df_new = pd.read_csv('latest_listings.csv')
        #luetaan viimeisin hakutulos dataframeen
        df_old = pd.read_csv(file_path)
        #print(df_old)
        #asetetaan kaikki oletuksena ei-aktiivisiksi
        df_old['active'] = False
        #päivitetään rivit, jotka löytyvät uudesta hausta
        df_old.loc[df_old['url'].isin(url_list), 'active'] = True
        #Asetetaan df['removal_date'] arvoksi kuluva päivä, jos se on tyhjä ja df['active] = False
        df_old.loc[(df_old['removal_date'].isna()) & (df_old['active'] == False), 'removal_date'] = datetime.today().date()
    
        #yhdistetään uudet rivit, jotka eivät ole vielä mukana
        df_combined = pd.concat([
            df_old,
            df_new[~df_new['url'].isin(df_old['url'])]
        ], ignore_index=True)
    else:
        #Tiedostoa ei ole, käytetään vain uusia
        df_combined = pd.read_csv('latest_listings.csv')
        #poistetaan duplikaatot
    df_combined.drop_duplicates(subset = 'url', keep = 'last', inplace = True)
    #Tallennetaan df csv
    df_combined.to_csv(file_path, index = False)
    return df_combined

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
        wait_random()
    driver.quit()

    date = current_date()
    #filename = f"{date}_listings.csv"

    df = pd.DataFrame(url_list, columns=['url'])
    df['fetch_date'] = current_date()
    df['active'] = True
    df['removal_date'] = None
    #print(df['removal_date'])
    df = df.drop_duplicates(subset = ['url'], keep = 'last')


    print(f"Writing {len(url_list)} rows to csv")
    df.to_csv("latest_listings.csv", index=False)
    print("Save complete!")

    end_time_etuovi = time.time()
    execution_time_etuovi = end_time_etuovi - start_time_etuovi
    print(f"Execution time: {execution_time_etuovi:.2f} seconds")

def get_soup(df):
    soups = []


    for index, row in df.iterrows():
        url = row['url']
        try:
            #print(f"Fetching: {url}")
            response = requests.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                soups.append(str(soup))  # tallenna tekstinä
            else:
                soups.append(None)
                print(f"Failed with status code {response.status_code}")
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            soups.append(None)

        wait_random()

    df['soup'] = soups
    return df

def extract_price(soup):
    soup = BeautifulSoup(soup, 'html.parser')
    try:
        h3_tags = soup.find_all('h3')
        if not h3_tags:
            return 0
        hinta_str = h3_tags[0].get_text(strip=True).replace('\xa0', '').replace('€', '').strip()
        hinta = int(hinta_str)

    except Exception:
        hinta = 0
    return hinta

def extract_address(soup):
    soup = BeautifulSoup(soup, 'html.parser')
    try:
        h1_tags = soup.find_all('h1')
        print(h1_tags)
        if not h1_tags:
            return 0
        address_str = h1_tags[0].get_text(strip=True).replace('\xa0', '').replace('€', '').strip()
        address = address_str

    except Exception:
        address = ""
    return address

def extract_em_span_pairs(soup):
    if isinstance(soup, str):
        soup = BeautifulSoup(soup, 'html.parser')

    em_dict = {}
    try:
        em_tags = soup.find_all('em')
        #em_tags = em_tags[0:10]
        for em_tag in em_tags:
            key = em_tag.get_text(strip=True)
            value = em_tag.find_next('span').get_text(strip = True)

            if len(value) > 0:
                em_dict[key] = value
            else:
                em_dict[key] == ''

    except Exception as e:
        print(f"extract_em_text_pairs error: {e}")
        em_dict = {}
    return em_dict


if __name__ == "__main__":
    base_url = 'https://www.etuovi.com/myytavat-asunnot/oulu/heinapaa?haku=M2284191086'
    page = 1
    seen_hrefs = set()
    url_list = []
    #Haetaan listausten osoitteet, tallennetaan ne latest_listings.csv
    get_urls(base_url, page) 

    temp_df = pd.read_csv('latest_listings.csv')
    url_list = temp_df['url']
    print(f"Calling function update_listing_file with {len(url_list)} rows")
    df_combined = update_listing_file(url_list)
    print(f"Function update_listing_file returnd a dataframe with {len(df_combined)} values")
    
    #Luodaan df niistä riveistä, joita puuttuu hinta ja haetaan SOUP niille
    try:
        df_no_values = df_combined[df_combined['price'].isna()].copy()
        df_no_values = get_soup(df_no_values)
        df_combined.update(df_no_values)

    except KeyError:
        df_combined = get_soup(df_combined)
    #Yhdisteään haetut tiedot takaisin
    #print(df_combined.head()) #DEBUG

    #TAllennetaan väliaikaisesti testiä varten df_combined csv:ksi, jotta ei tarvitse tehdä etuovesta hakuja testiä varten
    df_combined.to_csv("csv_with_soup_temp.csv")
    df_combined = pd.read_csv('csv_with_soup_temp.csv')
    #print(df_combined.head()) #DEBUG
    #TEHDÄÄN VÄLIAIKAISESTI lyhyt DF
    #df_combined =df_combined.head(1)
    #soup = df_combined['soup']

    #Haetaan hinta ja muut parametrit


    def process_listing(soup):
        return {
            'price': extract_price(soup),
            **extract_em_span_pairs(soup),
            'address': extract_address(soup)
        }

    for idx, row in df_combined.iterrows():
        data = process_listing(row['soup'])
        for key, value in data.items():
            df_combined.at[idx, key] = value

    for idx, row in df_combined.iterrows():
        data = extract_em_span_pairs(row['soup'])

    #print(df_combined.columns)
    df_combined.drop(columns = ['Muut maksut','Hinta','Rakennusvuosi','soup','Omistusmuoto','Huoneita','Lisätietoja pinta-alasta','Vapautuminen','Parvekkeen kuvaus','Asuntoon kuuluu','Ilmanvaihto','Rakennus- ja pintamateriaalit','Keittiön kuvaus','Kylpyhuoneen kuvaus', 'Olohuoneen kuvaus', 'Makuuhuoneiden kuvaus',
       'Säilytystilojen kuvaus', 'Kattotyyppi', 'Kattomateriaali','Isännöitsijän yhteystiedot', 'Huolto',
       'Taloyhtiöön kuuluu','Energialuokka','Sauna','Parveke','Hissi',
       'Tontin koko','Kaavoitustilanne', 'Tontin vuokraaja','Palvelut', 'Liikenneyhteydet', 'Näkymät',
       'Kokonaispinta-ala', 'Käyttöönottovuosi', 'Lisätietoja kunnosta',
       'Kattomateriaalin kuvaus', 'Muuta taloyhtiöstä','Huoneistoselitelmä','Vastike',
       'Taloyhtiön autopaikat', 'Kaavoitustiedot', 'Lisätietoja',
       'Tietoliikenne', 'Kohteen lisätiedot', 'Vesihuollon kuvaus', 'Viemäri',
       'Tiedustelut', 'Muuta kauppaan kuuluvaa', 'WC-tilojen kuvaus',
       'Saunan kuvaus', 'Kattotyypin kuvaus', 'Lisätietoa auton säilytyksestä',
       'Tontin vuokra', 'Tulisija', 'Tilojen kuvaus', 'Asbestikartoitus',
       'Kodinhoitohuoneen kuvaus', 'Kiinteistötunnus', 'Pihan kuvaus',
       'Asuinkerrosten määrä', 'Lämmitysjärjestelmä', 'Vesijohto',
       'Asunnon käytössä olevat autopaikat', 'Lisätietoa tontin omistuksesta','Lisätietoa tontista', 'Kuntotarkastus', 'Ranta',
       'Ajo-ohjeet'], inplace = True)
    
    df_combined['huoneita'] = df_combined['Tyyppi'].str[0]
    df_combined['tontin_vuokra-aika'] = df_combined['Tontin vuokra-aika päättyy'].fillna(df_combined['Tontin vuokra-aika'])
    df_combined.drop(columns=['Tontin vuokra-aika','Tontin vuokra-aika päättyy'],inplace = True)


    #print(df_combined)
    df_combined.to_csv("riisuttu.csv")

     
