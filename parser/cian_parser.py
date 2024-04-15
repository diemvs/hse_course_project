from dotenv import load_dotenv
import pandas as pd
from selenium import webdriver 
from selenium.webdriver.common.by import By
import os
import urllib.parse
from urllib.parse import urljoin, urlencode

from districts import District
from utils import enum_to_int

DEFAULT_PATH="kupit-kvartiru-1-komn-ili-2-komn"

class SimpleCianParser():
    # CIAN url
    __url = None
    
    def __init__(self):
        # take environment variables from .env
        load_dotenv()
        # take CIAN_URL variavle from .env
        self.__url = os.environ.get('CIAN_URL')
        
    def build_url(
            self, 
            path: str = DEFAULT_PATH, 
            params: dict = {}
        ) -> str:
        query = "?" + urlencode(params)
        
        return urljoin(self.__url, path + query)
    
    def parse(self, url: str, images_cnt: int) -> pd.DataFrame:
        # create the pandas DataFrame
        df = pd.DataFrame([], columns=['url'])
        # create the driver
        driver = webdriver.Chrome()
        # loading the web page
        driver.get(url)
        # finding flat list component
        flat_list_ex = "/html/body/div[1]/div/div[6]"
        flat_list = driver.find_element(By.XPATH, flat_list_ex)
        # getting flat component
        for flat in flat_list.find_elements(By.XPATH, '//div/div'):
            # getting images list component
            img_list = flat.find_element(By.XPATH, '//article/div[1]/a/div[1]/div/ul')
            
            for img in img_list.find_elements(By.XPATH, '//li/img'):
                src = img.get_attribute('src')
                
                df.loc[-1] = src
                df.index = df.index + 1
                df = df.sort_index()
                
                if df.shape[0] == images_cnt:
                    return df
        return df
    
    def get_flat_images(
        self, 
        images_cnt = 100, 
        districts: list[District] = []
    ) -> pd.DataFrame:
        url = ""
        
        if(len(districts) == 0):
            url = self.build_url()
        else:
            # setting params
            params = dict(
                deal_type = 'sale',
                engine_version = 2,
                offer_type = 'flat'
            )
            # todo: remove this loop
            for idx, d in enumerate(districts):
                params[f'district[{idx}]'] = enum_to_int(d)
            # build the url with params
            url = self.build_url(path="cat.php", params=params)
        
        # parsing thr website
        result = self.parse(url, images_cnt)
        
        return result
       
        