!pip install selenium
!apt-get update
!apt-get install -y chromium-browser
!apt-get install chromium chromium-driver
!pip install webdriver-manager
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait,Select
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from IPython.display import Image, display
from google.colab import output
import re
import base64
import time
output.clear()