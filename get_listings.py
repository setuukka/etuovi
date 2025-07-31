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
import os

poistettavat_sarakkeet = ['Unnamed: 0','Sijainti','Omistusmuoto',
       'Huoneistoselitelmä', 'Huoneita', 'Lisätietoja pinta-alasta', 'Rakennusvuosi', 'Käyttöönottovuosi', 'Vapautuminen', 'Hinta',
       'Vastike', 'Muut maksut', 'Sauna', 'Hissi', 'Asunnon kunto',
       'Lämmitysjärjestelmän kuvaus', 'Rakennus- ja pintamateriaalit',
       'Keittiön kuvaus', 'Kylpyhuoneen kuvaus', 'Olohuoneen kuvaus',
       'Säilytystilojen kuvaus', 'Kattotyyppi', 'Kattomateriaali',
       'Kattomateriaalin kuvaus',  'Huolto', 'Taloyhtiöön kuuluu',
       'Tehdyt remontit', 'Tulevat remontit', 'Energialuokka', 'Tontin koko','Kaavoitustilanne', 'Tontin vuokra',
       'Tontin vuokraaja', 'Parveke', 'Parvekkeen kuvaus', 'Tietoliikenne', 'Kohteen lisätiedot',
       'Muuta taloyhtiöstä', 'Taloyhtiön autopaikat', 'Palvelut',
       'Liikenneyhteydet', 'Tiedustelut', 'Makuuhuoneiden kuvaus',
       'Kaavoitustiedot', 'Lisätietoa auton säilytyksestä', 'Saunan kuvaus',
       'Vesihuollon kuvaus', 'Viemäri', 'Asuntoon kuuluu', 'Ilmanvaihto',
       'Näkymät', 'Lisätietoja kunnosta', 'Lisätietoja',
       'Muuta kauppaan kuuluvaa', 'WC-tilojen kuvaus', 'Kattotyypin kuvaus',
       'Tulisija', 'Tilojen kuvaus', 'Asbestikartoitus',
       'Kodinhoitohuoneen kuvaus', 'Kiinteistötunnus', 'Pihan kuvaus',
       'Asuinkerrosten määrä', 'Lämmitysjärjestelmä', 'Vesijohto',
       'Asunnon käytössä olevat autopaikat', 'Lisätietoa tontin omistuksesta',
       'Lisätietoa tontista', 'Ajo-ohjeet','Taloyhtiön nimi','Isännöitsijän yhteystiedot','Kokonaispinta-ala']
try:
    print("Käyttäjä:", os.getlogin())
    print("HOME:", os.environ.get("HOME"))
except FileNotFoundError:
    print("We are not in Linux")

debug_printing = False
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
firefox_options.headless = True
print("Headless-tile:", firefox_options.headless)
firefox_options.set_preference("layers.acceleration.disabled", True)  # Poistaa GPU-kiihdytyksen
firefox_options.set_preference("media.hardware-video-decoding.enabled", False)

if not os.path.exists(geckodriver_path):
    raise FileExistsError(f"Geckodriver not found at {geckodriver_path}")

print("Luodaan selainobjekti..")
driver = webdriver.Firefox(service = Service(geckodriver_path),options = firefox_options)
print("Selainobjekti luotu!")


def wait_random():
    wait_time = random.uniform(1, 5)
    print(f"Waiting for {wait_time:.2f} seconds")
    time.sleep(wait_time)

def update_listing_file(url_list, filename='all_listings.csv'):
    file_path = Path(filename)
    if file_path.exists():

        df_new = pd.read_csv('latest_listings.csv')
        if debug_printing:
            print(f"read {len(df_new)} listings to compare to old listings")
        #luetaan viimeisin hakutulos dataframeen
        df_old = pd.read_csv(file_path)
        if debug_printing:
            print(f"Old dataframe contains {len(df_old)} listings")
        #asetetaan kaikki oletuksena ei-aktiivisiksi
        if debug_printing:
            print(f"Old df has {len(df_old['active'])} listings. Setting all to False")
        df_old['active'] = False
        if debug_printing:
            print(f"{df_old['active'].value_counts()}")
        #päivitetään rivit, jotka löytyvät uudesta hausta
        df_old.loc[df_old['url'].isin(url_list), 'active'] = True
        if debug_printing:
            print(f"Old df now has {len(df_old['active'])} listings, after setting still excisting to True")
        #Asetetaan df['removal_date'] arvoksi kuluva päivä, jos se on tyhjä ja df['active] = False
        df_old.loc[(df_old['removal_date'].isna()) & (df_old['active'] == False), 'removal_date'] = datetime.today().date()
        if debug_printing:
            print(f"{len(df_old['active'] == False)} items set to False and deactive")
        #yhdistetään uudet rivit, jotka eivät ole vielä mukana
        df_combined = pd.concat([
            df_old,
            df_new[~df_new['url'].isin(df_old['url'])]
        ], ignore_index=True)
        if debug_printing:
            print(f"df_combined has {len(df_combined)} rows. old_df had{len(df_old)} rows. Change is {len(df_combined) - len(df_old)} rows")
    else:
        if debug_printing:
            print(f"Old file was not found. Using only today's listings")
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
    print("Siirrytään sivulle..")
    driver.get(base_url)
    print("Sivu ladattu!")
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
        if debug_printing:
            print(f"getting soup for: {url}")
        try:
            #print(f"Fetching: {url}")
            response = requests.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                soups.append(str(soup))  # tallenna tekstinä
                if debug_printing:
                    print(f"Got response status code {response.status_code} and added soup number {len(soups)} to soups list ") 
            else:
                soups.append(None)
                print(f"Failed with status code {response.status_code}")
                if debug_printing:
                    print(f"Soup failed with code {response.status_code}")
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            soups.append(None)

        wait_random()
    df['soup'] = soups
    return df

def extract_price(soup):
    if debug_printing:
        print(f"We are in extract_price function")
    try:
        soup = BeautifulSoup(soup, 'html.parser')
    except TypeError:
        if debug_printing:
            print(f"We got TypError while soup = BeautifulSoup(soup, 'html.parser')")
        hinta = 0
    try:
        h3_tags = soup.find_all('h3')
        if not h3_tags:
            if debug_printing:
                print("No H3 tags were found to extract price from")
            return 0
        hinta_str = h3_tags[0].get_text(strip=True).replace('\xa0', '').replace('€', '').strip()
        hinta = int(hinta_str)
        if debug_printing:
            print(f"Hinta_str is {hinta_str} and Hinta is {hinta}")

    except Exception:
        hinta = 0
    return hinta

def extract_address(soup):

    try:
        soup = BeautifulSoup(soup, 'html.parser')
    except TypeError:
        address = ""
    try:
        h1_tags = soup.find_all('h1')
        #print(h1_tags)
        if not h1_tags:
            return 0
        address_str = h1_tags[0].get_text(strip=True).replace('\xa0', '').replace('€', '').strip()
        address = address_str

    except Exception:
        address = ""
    return address

def extract_em_span_pairs(soup):
    em_dict = {}
    try:
        soup = BeautifulSoup(soup, 'html.parser')
    except TypeError:
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

def extract_em_div_pairs(soup):
    em_dict = {}
    try:
        soup = BeautifulSoup(soup, 'html.parser')
    except TypeError:
        em_dict = {}
    try:
        em_tags = soup.find_all('em')
        #em_tags = em_tags[0:10]
        for em_tag in em_tags:
            key = em_tag.get_text(strip=True)
            value = em_tag.find_next('div').get_text(strip = True)

            if len(value) > 0:
                em_dict[key] = value
            else:
                em_dict[key] == ''

    except Exception as e:
        print(f"extract_em_div_pairs error: {e}")
        em_dict = {}
    return em_dict

def extract_hoitovastike(soup):
    try:
        soup = BeautifulSoup(soup, 'html.parser')
    except TypeError:
        hoitovastike = float(0.0)
    try:
        hoitovastike = soup.find_all('p')
        hoitovastike = str(hoitovastike)
        hoitovastike = hoitovastike.split('Hoitovastike')[1][:100]
        hoitovastike = re.search(r'\d{1,3},\d{2}', hoitovastike)
        hoitovastike = float(hoitovastike.group().replace(',','.'))
    except Exception as e:
        hoitovastike = float(0.0)
    return hoitovastike

def extract_yhtiovastike_yhteensa(soup):

    try:
        soup = BeautifulSoup(soup, 'html.parser')
    except TypeError:
        yhtiovastike_yhteensa = float(0.0)
    try:
        yhtiovastike_yhteensa = soup.find_all('p')
        yhtiovastike_yhteensa = str(yhtiovastike_yhteensa)
        yhtiovastike_yhteensa = yhtiovastike_yhteensa.split('Yhtiövastike yhteensä')[1][:100]
        yhtiovastike_yhteensa = re.search(r'\d{1,3},\d{2}', yhtiovastike_yhteensa)
        yhtiovastike_yhteensa = float(yhtiovastike_yhteensa.group().replace(',','.'))
    except Exception as e:
        yhtiovastike_yhteensa = float(0.0)
    return yhtiovastike_yhteensa

def extract_year_built(soup):
    if debug_printing:
        print(f"We are in extract_year_built function")
    try:
        soup = BeautifulSoup(soup, 'html.parser')
    except TypeError:
        if debug_printing:
            print(f"We got TypError while soup = BeautifulSoup(soup, 'html.parser')")
        valmistusvuosi = 0
    try:
        h3_tags = soup.find_all('h3')
        if not h3_tags:
            if debug_printing:
                print("No H3 tags were found to extract price from")
            return 0
        valmistusvuosi = int(h3_tags[2].get_text())
        if debug_printing:
            print(f"Valmistusvuosi on {valmistusvuosi}")

    except Exception:
        valmistusvuosi = 0
    return valmistusvuosi

if __name__ == "__main__":
    base_url = 'https://www.etuovi.com/myytavat-asunnot/oulu/heinapaa?haku=M2284191086'
    page = 1
    seen_hrefs = set()
    url_list = []
    get_urls(base_url, page) #Haetaan listausten osoitteet, tallennetaan ne latest_listings.csv


    temp_df = pd.read_csv('latest_listings.csv')
    url_list = temp_df['url']
    if debug_printing:
        print(f"Calling function update_listing_file with {len(url_list)} rows")
    df_combined = update_listing_file(url_list)
    if debug_printing:
        print(f"Function update_listing_file returnd a dataframe with {len(df_combined)} values")
    
    #TAllennetaan väliaikaisesti testiä varten df_combined csv:ksi, jotta ei tarvitse tehdä etuovesta hakuja testiä varten
    #df_combined.to_csv("csv_with_soup_temp.csv")
    #df_combined = pd.read_csv('csv_with_soup_temp.csv')

    #Luodaan df niistä riveistä, joita puuttuu hinta ja haetaan SOUP niille
    try:
        df_no_values = df_combined[df_combined['hinta'].isna()].copy()
        if debug_printing:
            print(f"Created a dataframe of missing values with {len(df_no_values)} rows")

            jatka = input("Paina 'y' jatkaaksesi: ")
            if jatka.lower() != "y":
                print("Keskeytetään.")
                exit()  # tai sys.exit()


        df_no_values = get_soup(df_no_values)
        df_combined.update(df_no_values)

    except KeyError:
        if debug_printing:
            print(f"Got KeyError while creating missing prices dataframe!")
        df_combined = get_soup(df_combined)
    #Yhdisteään haetut tiedot takaisin
    #print(df_combined.head()) #DEBUG

    df_combined.to_csv("df_after_soup_debug.csv")    #Haetaan hinta ja muut parametrit


    def process_listing(soup):
        return {
            'hinta': extract_price(soup),
            'valmistusvuosi': extract_year_built(soup),
            **extract_em_div_pairs(soup),
            'address': extract_address(soup),
            'hoitovastike': extract_hoitovastike(soup),
            'yhtiovastike_yhteensa' : extract_yhtiovastike_yhteensa(soup)
        }

    for idx, row in df_combined.iterrows():
        try:
            data = process_listing(row['soup'])
            #if debug_printing:
                #print(f"idx={idx} keys: {list(data.keys())}")  # ✅ Tulosta mukana olevat kentät
            for key, value in data.items():
                df_combined.at[idx, key] = value
        except Exception as e:
            print(f"Error processing idx={idx}: {e}")
    for idx, row in df_combined.iterrows():
        data = extract_em_div_pairs(row['soup'])
    '''
    #print(df_combined.columns)
    df_combined = df_combined.drop(columns=poistettavat_sarakkeet, errors='ignore')    
    df_combined['huoneita'] = df_combined['Tyyppi'].str[0]
    df_combined['tontin_vuokra-aika'] = df_combined['Tontin vuokra-aika päättyy'].fillna(df_combined['Tontin vuokra-aika'])
    df_combined.drop(columns=['Tontin vuokra-aika','Tontin vuokra-aika päättyy'],inplace = True)
    #Otetaan osoitteesta vain katuosoite-osuus
    df_combined['katuosoite'] = df_combined['address'].str.split(',').str[0].str.strip()
    df_combined.drop(columns=['address'], inplace = True)
    #Muutetaan koko floatiksi
    df_combined['Asuintilojen pinta-ala'] = df_combined['Asuintilojen pinta-ala'].str.split(" ").str[0].str.replace(",",".")
    df_combined['Asuintilojen pinta-ala'] = df_combined['Asuintilojen pinta-ala'].astype(float)
    #Lasketaan neliöhinta ja -vastike
    try:
        df_combined['neliohinta'] = df_combined['hinta'] / df_combined['Asuintilojen pinta-ala']
    except KeyError:
        print(f"df_combined['hinta'] not found, KeyError")
    try:
        df_combined['neliovastike'] = df_combined['hoitovastike'] / df_combined['Asuintilojen pinta-ala']
    except:
        print("Error while calculating neliovastike")
    #print(df_combined)
    '''
    df_combined.to_csv("all_listings.csv")

    print(datetime.now())