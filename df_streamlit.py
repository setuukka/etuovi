import os
import time
import pandas as pd
from datetime import datetime
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
import plotly.express as px
import locale
#from geopy.geocoders import Nominatim
#import regex as re

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
df = pd.read_csv("df_for_streamlit.csv")
df = df.drop(columns = ['is_sauna', 'is_balcony','is_elevator'])

df['streetname_and_number'] = df['street'].astype(str) + " " + df['street_number'].astype(str)
#df = df.drop(columns = ['cond_adequate', 'cond_terrible', 'cond_unclassified'])

styled_df = df.style.background_gradient(subset=['hinta'], cmap='RdYlGn_r')

#Filter that returns the correct dataframe based on checkboxes
status = []
def dataframe_selector(df, active = True, passive = True, kv = True, rk = True, mo = True, hp = True, kmm = True):
    allowed_active = []
    allowed_districts = []
    if active:
        allowed_active.append(True)
    if passive:
        allowed_active.append(False)

    if kv:
        allowed_districts.append('kaukovainio')
    if rk:
        allowed_districts.append('Rajakylä')
        allowed_districts.append('rajakyla')
    if mo:
        allowed_districts.append('myllyoja')
    if hp:
        allowed_districts.append('heinapaa')
    if kmm:
        allowed_districts.append('kmm')

    mask = df['active'].isin(allowed_active) & df['district'].isin(allowed_districts)
    return df[mask]


aktiiviset = df[df['active'] == True]
poistuneet = df[df['active'] == False]

kadun_mukaan = df.groupby(['street']).agg(
    halvin =('price','min'),
    kallein = ('price', 'max')
)

if lit:
    st.sidebar.subheader("Number of rooms")
    yksio_checkbox = st.sidebar.checkbox(label = "1h", value=True)
    kaksio_checkbox = st.sidebar.checkbox(label = "2h", value=True)
    kolmio_checkbox = st.sidebar.checkbox(label = "3h", value=True)
    nelio_checkbox = st.sidebar.checkbox(label = "4h", value=True)
    muut_checkbox = st.sidebar.checkbox(label = "4+h", value=True)
    st.sidebar.subheader("Active / Passive")
    active_checkbox = st.sidebar.checkbox(label = "Active listings", value = True)
    passive_checkbox = st.sidebar.checkbox(label = "Passive listings", value = True)
    st.sidebar.subheader("District")
    kaukovainio_checkbox = st.sidebar.checkbox(label = "kaukovainio", value = True)
    rajakyla_checkbox = st.sidebar.checkbox(label = "rajakyla", value = True) 
    myllyoja_checkbox = st.sidebar.checkbox(label = "myllyoja", value = True) 
    heinapaa_checkbox = st.sidebar.checkbox(label = "heinapaa", value = True) 
    kmm_checkbox = st.sidebar.checkbox(label = "Kaakkuri, Metelinkangas", value = True) 

    #df_rows = df.shape[0]
    #df_columns = df.shape[1]

    df = dataframe_selector(df, active=active_checkbox, passive=passive_checkbox, kv = kaukovainio_checkbox, rk = rajakyla_checkbox, mo = myllyoja_checkbox, hp = heinapaa_checkbox, kmm = kmm_checkbox)
    
    tab1, tab2, tab3, tab4 = st.tabs(["Grouped by room count", "Colored", "Boxplot", "Grouped by street"])

    with tab1:
        st.write(df)
        #st.write(f"Rows {df_rows}, columns {df_columns}")
        #st.write(df.shape)
        if yksio_checkbox:
            st.write("One room")
            yksio = df[df['rooms'] == 1]
            st.write(yksio)
            st.write(yksio.describe())
        if kaksio_checkbox:
            st.write("Two rooms")
            kaksio = df[df['rooms'] == 2]
            st.write(kaksio)
            st.write(kaksio.describe())
        if kolmio_checkbox:
            st.write("Three rooms")
            kolmio = df[df['rooms'] == 3]
            st.write(kolmio)            
            st.write(kolmio.describe())
        if nelio_checkbox:
            st.write("Four rooms")
            nelio = df[df['rooms'] == 4]
            st.write(nelio)
            st.write(nelio.describe())
        if muut_checkbox:
            st.write("Five and more rooms")
            muut_koot = df[df['rooms'] > 4]
            st.write(muut_koot)
            st.write(muut_koot.describe())
        st.write("Unkown rooms")
        koottomat = df[df['rooms'] == 0]
        st.write(koottomat)

    with tab2:
        styled_df = df.style.format({
            'price': format_finnish,
            'price per sqm': format_finnish,
            'maintenance fee': format_finnish,
            'maintenance fee per sqm': format_finnish,
        }).background_gradient(subset=['price','price_sqm','maintenance_fee','maintenance_sqm'], cmap='RdYlGn_r')

        st.dataframe(styled_df)

    with tab3:
        fig = px.box(
            df, x = 'rooms', y = 'price', points = 'all')
        st.write(fig)

        df_by_street = df.sort_values(by = ['streetname_and_number','staircase'])
        df_by_street = df_by_street[['streetname_and_number','staircase','rooms','price','price_sqm','maintenance_fee','apartment_size']]
        st.dataframe(df_by_street)


    with tab4:
        df = df.sort_values(by = ['streetname_and_number'])
        for street in df['streetname_and_number'].unique():
            st.write(f"### {street}")
            st.dataframe(df[df['streetname_and_number'] == street], use_container_width=True)

    

