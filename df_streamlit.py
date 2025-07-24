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
import streamlit as st
import matplotlib.pyplot as plt

import locale
locale.setlocale(locale.LC_ALL, 'fi_FI.UTF-8')

def format_finnish(x):
    try:
        return locale.format_string("%.2f", x, grouping=True)
    except:
        return x
    
lit = True

st.set_page_config(layout = "wide")
df = pd.read_csv("all_listings.csv")

df = df.drop(columns = ['Unnamed: 0','Taloyhtiön nimi','Isännöitsijän yhteystiedot'], errors = 'ignore')

#df['huoneita'] == df['huoneita'].astype(int)
df = df[['url','huoneita','hinta','neliohinta','hoitovastike','neliovastike','yhtiovastike_yhteensa','katuosoite','Tyyppi', 'Asuintilojen pinta-ala', 'Kerrokset', 'Tontin omistus','active']]
df['huoneita'] = pd.to_numeric(df['huoneita'], errors='coerce').fillna(0).astype(int)


styled_df = df.style.background_gradient(subset=['hinta'], cmap='RdYlGn_r')


aktiiviset = df[df['active'] == True]
poistuneet = df[df['active'] == False]

yksio = df[df['huoneita'] == 1]
kaksio = df[df['huoneita'] == 2]
kolmio = df[df['huoneita'] == 3]

nelio = df[df['huoneita'] == 4]
muut_koot = df[df['huoneita'] > 4]
koottomat = df[df['huoneita'] == 0]

if lit:
    tab1, tab2, tab3 = st.tabs(["Huoneiden määrän mukaan", "Väritetty", "Owl"])

    with tab1:
        st.write("Yksiöt")
        st.write(yksio)
        st.write("Kaksiot")
        st.write(kaksio)
        st.write("Kolmiot")
        st.write(kolmio)
        st.write("Neliot")
        st.write(nelio)
        st.write("Vielä suuremmat")
        st.write(muut_koot)
        st.write("Koottomat")
        st.write(koottomat)

    with tab2:
        styled_df = df.style.format({
            'hinta': format_finnish,
            'neliohinta': format_finnish,
            'hoitovastike': format_finnish,
            'neliovastike': format_finnish,
        }).background_gradient(subset=['hinta','neliohinta','hoitovastike','neliovastike'], cmap='RdYlGn_r')

        st.dataframe(styled_df)