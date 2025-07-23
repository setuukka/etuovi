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


df = pd.read_csv("all_listings.csv")
df.drop(columns=['soup'], inplace = True)
print(df.head(3))
df = df[[]]
print(df.columns)