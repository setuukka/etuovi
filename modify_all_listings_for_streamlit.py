# %%
import pandas as pd
import numpy as np
from datetime import datetime

# %%
df = pd.read_csv('all_listings.csv')

# %%
#Drop unnecessary columns
df.drop(columns = ['soup','Kohdenumero','Sijainti','Tyyppi','Omistusmuoto','Huoneita','Käyttöönottovuosi',
                    'Parvekkeen kuvaus','Kokonaispinta-ala','Lisätietoja pinta-alasta','Tietoliikenne','Lämmitysjärjestelmän kuvaus','Rakennus- ja pintamateriaalit',
                    'Keittiön kuvaus','Hinta','Kylpyhuoneen kuvaus', 'Saunan kuvaus', 'Olohuoneen kuvaus','Vastike',
                    'Makuuhuoneiden kuvaus', 'Kattotyyppi', 'Kattomateriaalin kuvaus','Isännöitsijän yhteystiedot', 
                    'Huolto','Taloyhtiöön kuuluu', 'Muuta taloyhtiöstä', 'Tehdyt remontit','Tulevat remontit',
                    'Energialuokka', 'Tontin koko', 'Kaavoitustiedot', 'Kaavoitustilanne', 'Tontin vuokra',
                    'Tontin vuokraaja', 'Tontin vuokra-aika päättyy','Lisätietoa auton säilytyksestä','Muut maksut',
                    'Vapautuminen', 'Kohteen lisätiedot','Asbestikartoitus', 'Taloyhtiön autopaikat', 'valmistusvuosi',
                    'WC-tilojen kuvaus','Kodinhoitohuoneen kuvaus', 'Kattomateriaali', 'Säilytystilojen kuvaus',
                    'Palvelut', 'Liikenneyhteydet', 'Tiedustelut', 'Vesihuollon kuvaus','Viemäri', 
                    'Asuntoon kuuluu', 'Ilmanvaihto', 'Näkymät','Lisätietoja kunnosta', 'Lisätietoja',
                    'Muuta kauppaan kuuluvaa','Kattotyypin kuvaus', 'Tulisija', 'Tilojen kuvaus','Kiinteistötunnus',
                    'Pihan kuvaus','Asuinkerrosten määrä', 'Lämmitysjärjestelmä','Vesijohto','Huoneistoselitelmä',
                    'Asunnon käytössä olevat autopaikat','Lisätietoa tontin omistuksesta', 'Tontin vuokra-aika', 
                    'Ajo-ohjeet','Muiden tilojen pinta-ala'], inplace = True, errors = 'ignore')

# %%
#correct data types of dates to make calcutations on sale times
df['removal_date'] = pd.to_datetime(df['removal_date'], format="%Y-%m-%d", errors='coerce')
df['fetch_date'] = pd.to_datetime(df['fetch_date'], format="%d%m%Y", errors='coerce')
#Create sell_time_days variable
df['sell_time_days'] = (df['removal_date'] - df['fetch_date']).dt.days

# %%
#extractin street address from full address
df['street'] = df['address'].str.split(',').str[0].str.strip()
df.drop(columns=['address'], inplace = True)


# %%
#Convert apartment size to float
df['apartment_size'] = df['Asuintilojen pinta-ala'].str.split(" ").str[0].str.replace(",",".")
df['apartment_size'] = df['apartment_size'].astype(float)
df.drop(columns = (['Asuintilojen pinta-ala']), inplace = True)

# %%
#Calculate square meter price
try:
    df['price_sqm'] = df['hinta'] / df['apartment_size']
except KeyError:
    print(f"df['hinta'] not found, KeyError")
try:
    df['maintenance_sqm'] = df['hoitovastike'] / df['apartment_size']
except:
    print("Error while calculating maintenance_sqm")

# %%
#Create variable for number of rooms
df['rooms'] = pd.to_numeric(df['huoneita'], errors='coerce').fillna(0).astype(int)
df.drop(columns = ['huoneita'], inplace = True)

# %%
#Create streetname, streetnumber and staircase variables
df[['street', 'street_number', 'staircase']] = df['street'].str.extract(r'^(.*?)[ ]*(\d+)[ ]*([A-Za-z]?)$')
df['street'] = df['street'].apply(lambda x : str(x).split()[0])
df['street_number'] = pd.to_numeric(df['street_number'], errors='coerce').fillna(0).astype(int)

# %%
df.rename(columns = {'Rakennusvuosi' : 'year_built', 'hinta': 'price', 'Kerrokset' : 'total_floors', 'Sauna' : 'sauna', 'Parveke' : 'balcony',
       'Hissi' : 'elevator', 'Asunnon kunto' : 'condition', 'Taloyhtiön nimi' : 'housing_company', 'Tontin omistus' : 'plot_ownership',
       'hoitovastike' : 'maintenance_fee', 'yhtiovastike_yhteensa' : 'total_maintenance', 'huoneita' : 'rooms'}, inplace = True)

# %%
#Muodostetaan boolean muuttujat muutamasta parametrista
df['is_sauna'] = df['sauna'].map(lambda x : 1 if x == 'Asunnossa on sauna' else 0)
df['is_balcony'] = df['balcony'].map(lambda x : 1 if x == 'Asunnossa on parveke' else 0)
df['is_elevator'] = df['elevator'].map(lambda x : 1 if x == 'Taloyhtiössä on hissi' else 0)
df.drop(columns = (['sauna','balcony','elevator']), inplace = True)

# %%
#Format some numeric values
df['price'] = df['price'].apply(lambda x : int(x))
df['total_maintenance'] = df['total_maintenance'].apply(lambda x : round(x,2))
df['price_sqm'] = df['price_sqm'].apply(lambda x : round(x,2))
df['maintenance_sqm'] = df['maintenance_sqm'].apply(lambda x : round(x,2))

# %%
#Create decade built column
df['decade_built'] = df['year_built'].apply(lambda x : int(str(x)[:3]+"0"))

# %%
#sorting columns
df = df[['url', 'year_built', 'rooms', 'apartment_size', 'price', 'price_sqm', 'maintenance_fee', 'maintenance_sqm', 'total_maintenance', 'active', 'condition', 'street', 'street_number', 'staircase', 'total_floors', 
       'housing_company', 'plot_ownership', 'fetch_date','removal_date', 'sell_time_days', 'decade_built', 'is_sauna', 'is_balcony', 'is_elevator']]

# %%

#Renaming values to english
conditions_dict = {'Hyvä' : 'good', 'Tyydyttävä' : 'adequate', 'Huono' : 'terrible', 'Ei luokiteltu' : 'unclassified'}
df['condition'] = df['condition'].replace(conditions_dict)

plot_ownership_dict = {'Vuokra' : 'rental','Oma' : 'own'}
df['plot_ownership'] = df['plot_ownership'].replace(plot_ownership_dict)


# %%
#Creating dummy variables on condition. Base line is "hyvä", which means "Good"
df['condition'] = pd.Categorical(
    df['condition'],
    categories = ['good','adequate', 'terrible','unclassified'],
    ordered = True
)
condition_dummies = pd.get_dummies(
    df['condition'], 
    drop_first=True, 
    dtype = int,
    prefix = 'cond',
    prefix_sep = '_')
#print(condition_dummies)
#df = df.drop(columns = ['condition'])
df = pd.concat([df, condition_dummies], axis = 1)
# %%
df.to_csv("df_for_streamlit.csv", index = False)
print(f"csv for streamlit saved with {len(df)} rows on {datetime.now()}")
# %%



