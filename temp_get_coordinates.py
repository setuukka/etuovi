
import pandas as pd
from datetime import datetime
import numpy as np
import time
import locale
from geopy.geocoders import Nominatim


df = pd.read_csv("all_listings.csv")
df = df.drop(columns = ['soup','Unnamed: 0','Taloyhtiön nimi','Isännöitsijän yhteystiedot'], errors = 'ignore')

geolocator = Nominatim(user_agent="df_streamlit")

def get_coordinates(row):
    try:
        location = geolocator.geocode(row["katuosoite"] + ', Oulu')
        time.sleep(1)  # Hyvä käytäntö Nominatim-rajapinnassa
        if location:
            return pd.Series([location.latitude, location.longitude])
    except:
        return pd.Series([None, None])
    return pd.Series([None, None])
    
df[['lat', 'lon']] = df.apply(get_coordinates, axis = 1)

df['lat'] = df['lat'].fillna(65.00)
df['lon'] = df['lon'].fillna(25.00)

df.to_csv("all_listings_with_coordinates.csv")
print("Dataframe saved!")