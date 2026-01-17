from openai import OpenAI
import pandas as pd
import requests
from flask import Flask, request, jsonify
import os

def get_answer():

    answer = ['STATE', '20', 'Total population', 'P1_001N', 2020]

    CENSUS_API_KEY = os.getenv("CENSUS_API_KEY")
    

    api_key = CENSUS_API_KEY
    # Define the base URL for the Census API
    year = int(answer[4])
    base_url = f"https://api.census.gov/data/{str(year)}/dec/pl"

    census_data = None

    if year == 2000:
        if answer[0] == "COUNTY":
            state_code = answer[1][:2]
            county_code = answer[1][2:]

            # Sample: https://api.census.gov/data/2000/dec/pl?get=NAME,PL001006&for=county:025&in=state:55&key=REDACTED_CENSUS_KEY
            params = {
                "get": "NAME," + answer[3],
                "for": f"county:{county_code}",
                "in": f"state:{state_code}",
                "key": api_key,
            }

            response = requests.get(base_url, params=params)

            if response.status_code == 200:
                census_data = response.json()
                print(f"Census API response: {census_data}")
            else:
                raise Exception(f"Census API Error: {response.status_code}")

        elif answer[0] == "STATE":
            params = {
                "get": "NAME," + answer[3],
                "for": f"state:{answer[1]}",
                "key": api_key,
            }

            response = requests.get(base_url, params=params)

            if response.status_code == 200:
                census_data = response.json()
                print(f"Census API response: {census_data}")

    elif year == 2010:
        # sample: https://api.census.gov/data/2010/dec/sf1?get=NAME,P001001&for=county:025&in=state:55&key=...
        # sample: (STATE, 55, Total population, PL001001, 2000)
        if answer[0] == "COUNTY":
            state_code = answer[1][:2]
            county_code = answer[1][2:]

            params = {
                "get": "NAME," + answer[3],
                "for": f"county:{county_code}",
                "in": f"state:{state_code}",
                "key": api_key,
            }

            response = requests.get(base_url, params=params)

            if response.status_code == 200:
                census_data = response.json()
                print(f"Census API response: {census_data}")
            else:
                raise Exception(f"Census API Error: {response.status_code}")

        elif answer[0] == "STATE":
            params = {
                "get": "NAME," + answer[3],
                "for": f"state:{answer[1]}",
                "key": api_key,
            }

            response = requests.get(base_url, params=params)
            

            if response.status_code == 200:
                census_data = response.json()
                print(f"Census API response: {census_data}")

    elif year == 2020:
      
        # example: https://api.census.gov/data/2020/dec/pl?get=P1_001N&for=county:025&in=state:55
        if answer[0] == "COUNTY":
            state_code = answer[1][:2]
            county_code = answer[1][2:]

            params = {
                "get": answer[3],
                "for": f"county:{county_code}",
                "in": f"state:{state_code}",
                "key": api_key,
            }

            response = requests.get(base_url, params=params)
            

            if response.status_code == 200:
                census_data = response.json()
                print(f"Census API response: {census_data}")
            else:
                raise Exception(f"Census API Error: {response.status_code}")

        elif answer[0] == "STATE":
            params = {
                "get": answer[3],
                "for": f"state:{answer[1]}",
                "key": api_key,
            }

            response = requests.get(base_url, params=params)

            if response.status_code == 200:
                census_data = response.json()
                print(f"Census API response: {census_data}")
        
get_answer()
