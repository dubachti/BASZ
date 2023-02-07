import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
from config import API_key

ADDRESS = 'ADDRESS'
STREET = 'STREET'
ZIP = 'ZIP_CODE'
ROOMS = 'ROOMS'
SPACE = 'SPACE'
PRICE = 'PRICE'
APT_INFO = 'APT_INFO'
CYCLE_TIME = 'CYCLE_TIME'
CYCLE_DIST = 'CYCLE_DIST'
SCORE = 'SCORE'

attributes = {  
                ADDRESS: ('span', {'class': 'AddressLine__TextStyled-eaUAMD iBNjyG'}),
                APT_INFO: ('h3', {'class': 'Box-cYFBPY hKJGPR Heading-daBLVV dOtgYu'})  # rooms, space, price
             }

header = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"}

class HousingData():
    def __init__(self, num_pages: int = 1) -> None:
        self.df = self.load_data(num_pages=num_pages)

    def load_data(self, num_pages: int) -> pd.DataFrame:
        df = pd.DataFrame()

        for i in range(1,num_pages+1):
            print(f'proccesing page nr. {i}')
            link = f'https://www.immoscout24.ch/de/immobilien/mieten/ort-zuerich?pn={i}'

            req = requests.get(link, headers=header)
            if req.status_code == 404: break # ran out of pages
            assert req.status_code == 200, f'error in REST call: {req.status_code=}'
            req.encoding = 'UTF-8'

            soup = BeautifulSoup(req.text, 'html.parser')
            apts = soup.find_all('a', {'class': 'Wrapper__A-kVOWTT lfjjIW'})
            for apt in apts:
                apt_obj = {}

                # parse address field
                try:
                    address_info = apt.find(*attributes[ADDRESS]).text
                    address_info = address_info.split(', ')
                except:
                    address_info = []

                # handles non-consistent address notation 
                # (everything before zip code is recarded as street + nr.)
                for j, x in enumerate(address_info): 
                    if 'Zürich' in x:
                        apt_obj[STREET] = ''.join(address_info[:j])
                        apt_obj[ZIP] = address_info[j]
                        break
                else:
                    apt_obj[STREET] = ''.join(address_info[:-1])
                    apt_obj[ZIP] = None
           
                # parse apartment info
                try:
                    apt_info = apt.find(*attributes[APT_INFO]).text
                    apt_info = apt_info.split(', ')
                except:
                    apt_info = []

                apt_obj[ROOMS] = ([x for x in apt_info if 'Zimmer' in x]+[None])[0] # note: concat with none since apt's might have missing attributes
                apt_obj[SPACE] = ([x for x in apt_info if 'm²' in x]+[None])[0]
                apt_obj[PRICE] = ([x for x in apt_info if 'CHF' in x]+[None])[0]

                df = pd.concat([df, pd.DataFrame([apt_obj])], ignore_index=True)

        # strip numbers in column rooms, space, price and cast to float
        for col in ROOMS, SPACE, PRICE:
            df[col] = df[col].str.extract('([-+]?\d*\,?\d+)', expand=True)
            df[col] = df[col].str.replace(',', '.').astype(float)

        # strip numbers in column zip and cast to int
        df[ZIP] = df[ZIP].str.extract('([-+]?\d*\,?\d+)', expand=True)
        df[ZIP] = df[ZIP].str.replace(',', '.').astype(int)

        return df

    # calculates and appends cycling distance and time to ETH Zentrum using google directions API
    def append_cycling_dist(self, 
                            mode: str = 'cycling',
                            dest: str = 'ETH Zürich Hauptgebäude, Rämistrasse 101, 8092 Zürich'
                            ) -> None:

        time_column = []    
        dist_column = []
        dest = street.replace(' ', '+')

        print('calculating cycling time and dist')
        n = len(self.df[STREET])
        print('calculating cycling distance: ', end='')

        for i, (street, zip_num) in enumerate(self.df[[STREET, ZIP]]):

            if not i%(n//10): print('/', end='')

            start = street.replace(' ', '+') + f'+{zip_num}+Zürich'
            link = f'https://maps.googleapis.com/maps/api/directions/json?origin={start}&destination={dest}&mode={mode}&key={API_key}'
            try:
                req = requests.get(link)
                results = json.loads(req.content)
                legs = results.get('routes').pop(0).get('legs')
                time = legs[0].get('duration').get('value') # time in [s]
                dist = legs[0].get('distance').get('value') # distance in [m]
                time_column.append(time/60)
                dist_column.append(dist/1000)
            except:
                time_column.append(None)
                dist_column.append(None)        

        print() # formatting

        self.df[CYCLE_TIME] = time_column
        self.df[CYCLE_DIST] = dist_column