import pandas as pd

df = pd.read_csv("all_listings.csv")


'''df.iloc[13, df.columns.get_loc('huoneita')] = 2
df.iloc[20, df.columns.get_loc('huoneita')] = 1
df.iloc[45, df.columns.get_loc('huoneita')] = 2'''

#df.iloc[45, df.columns.get_loc('hinta')] = 90000





df.to_csv("all_listings.csv", index = False)

