import os
import time
import pandas as pd
from datetime import datetime
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
import plotly.express as px
import locale
from geopy.geocoders import Nominatim
import regex as re



try:
    locale.setlocale(locale.LC_ALL, 'fi_FI.UTF-8')
except:
    print("Locale not set")
def format_finnish(x):
    try:
        return locale.format_string("%.2f", x, grouping=True)
    except:
        return x
#set lit to false to run and debug python code
lit = True
if lit:
    st.set_page_config(layout = "wide")
df = pd.read_csv("all_listings.csv")

df = df.drop(columns = ['soup','Unnamed: 0','Taloyhtiön nimi','Isännöitsijän yhteystiedot'], errors = 'ignore')
poistettavat_sarakkeet = ['Unnamed: 0','Sijainti','Omistusmuoto',
       'Huoneita', 'Lisätietoja pinta-alasta', 'Rakennusvuosi', 'Käyttöönottovuosi', 'Vapautuminen', 'Hinta',
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

#muokataan dataframea
#print(df.columns)
#print(df.head(5))
#print(df['Huoneistoselitelmä'])
df = df.drop(columns=poistettavat_sarakkeet, errors='ignore')    
df['huoneita'] = df['Huoneistoselitelmä'].str[0]

df['tontin_vuokra-aika'] = df['Tontin vuokra-aika päättyy'].fillna(df['Tontin vuokra-aika'])
df.drop(columns=['Tontin vuokra-aika','Tontin vuokra-aika päättyy'],inplace = True)
#Otetaan osoitteesta vain katuosoite-osuus
df['katuosoite'] = df['address'].str.split(',').str[0].str.strip()
df.drop(columns=['address'], inplace = True)
#Muutetaan koko floatiksi
df['Asuintilojen pinta-ala'] = df['Asuintilojen pinta-ala'].str.split(" ").str[0].str.replace(",",".")
df['Asuintilojen pinta-ala'] = df['Asuintilojen pinta-ala'].astype(float)
#Lasketaan neliöhinta ja -vastike
try:
    df['neliohinta'] = df['hinta'] / df['Asuintilojen pinta-ala']
except KeyError:
    print(f"df_combined['hinta'] not found, KeyError")
try:
    df['neliovastike'] = df['hoitovastike'] / df['Asuintilojen pinta-ala']
except:
    print("Error while calculating neliovastike")
#print(df_combined)


#df['huoneita'] == df['huoneita'].astype(int)
#print(df.columns)
df = df[['url','huoneita','hinta','neliohinta','hoitovastike','neliovastike','yhtiovastike_yhteensa','katuosoite','Tyyppi', 'Asuintilojen pinta-ala', 'Kerrokset', 'Tontin omistus','active']]
df['huoneita'] = pd.to_numeric(df['huoneita'], errors='coerce').fillna(0).astype(int)
df[['katu', 'numero', 'kirjain']] = df['katuosoite'].str.extract(r'^(.*?)[ ]*(\d+)[ ]*([A-Za-z]?)$')
styled_df = df.style.background_gradient(subset=['hinta'], cmap='RdYlGn_r')

aktiiviset = df[df['active'] == True]
poistuneet = df[df['active'] == False]

yksio = df[df['huoneita'] == 1]
kaksio = df[df['huoneita'] == 2]
kolmio = df[df['huoneita'] == 3]

nelio = df[df['huoneita'] == 4]
muut_koot = df[df['huoneita'] > 4]
koottomat = df[df['huoneita'] == 0]

kadun_mukaan = df.groupby(['katuosoite','huoneita']).agg(
    halvin =('hinta','min'),
    kallein = ('hinta', 'max')
)

if lit:
    tab1, tab2, tab3 = st.tabs(["Huoneiden määrän mukaan", "Väritetty", "Kartalla"])

    with tab1:
        st.write("Yksiöt")
        st.write(yksio)
        st.write(yksio.describe())
        st.write("Kaksiot")
        st.write(kaksio)
        st.write(kaksio.describe())
        st.write("Kolmiot")
        st.write(kolmio)
        st.write(kolmio.describe())
        st.write("Neliot")
        st.write(nelio)
        st.write(nelio.describe())
        st.write("Vielä suuremmat")
        st.write(muut_koot)
        st.write(muut_koot.describe())
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

    with tab3:
        fig = px.scatter(
            df,
            x = 'huoneita',
            y = 'hinta',
            size = 'hoitovastike'

        )
        #event = st.plotly_chart(fig, key = 'iris', on_select = 'rerun')
        #event.selection
        #st.map(df[['lat', 'lon']])
        st.write(kadun_mukaan)