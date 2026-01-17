from openai import OpenAI
import pandas as pd
import requests
from flask import Flask, request, jsonify
import os

app = Flask(__name__)

csv_path = "Census/CensusVariables.csv"
data = pd.read_csv(csv_path)
csv_text = data.to_string(index=False)

CENSUS_API_KEY = os.getenv("CENSUS_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# OpenAI Client
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY is not set")
client = OpenAI(api_key=OPENAI_API_KEY)

@app.route('/process', methods=['POST'])
def process_data():
    data = request.get_json()
    #print("Data received from Node.js:", data)

    if "message" in data:
        print(f"message: {data['message']}")
        processed_message = get_answer(data["message"])
        print("Processed message:", processed_message)
        return jsonify({
            "originalMessage": data["message"],
            "processedMessage": processed_message,
        })
    else:
        print("Error: Missing 'message' key in request")
        return jsonify({"error": "Missing 'message' key"}), 400


def get_answer(prompt):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": """When responding, follow this exact format:
('geography LABEL', 'FIPS code', 'variable description', 'LABEL', Year).
Instructions:
1. Pick one geography and one variable from the CSV file provided.
2. For geography:
   - Use the LABEL from the CSV.
   - Provide the FIPS code for the selected geography.
3. For the variable:
   - Provide the description as listed in the CSV.
   - Include the LABEL of the variable.
4. Provide the year as specified in the table. The year's represent when census data was collected so choose the most appropriate year.
Ensure your response matches this format exactly.
         Example: (STATE, 55, Total population, PL001001, 2000)
         """},
            {"role": "user", "content": f"message: {prompt}, csv: {csv_text}"}
        ],
        max_tokens=100,
        temperature=0.1
    )

    # Remove parentheses from the answer
    answer = response.choices[0].message.content
    #print(f"Initial GPT response: {answer}")
    if answer[0] == "(" and answer[len(answer) - 1] == ")":
        answer = answer[1:len(answer) - 1]

    # Remove all single quotes from the list answer
    answer = list(answer)
    for i in answer:
        if i == "'":
            answer.remove("'")
    answer = "".join(answer)
    answer = answer.split(", ")

    # Your unique API key
    if not CENSUS_API_KEY:
        raise RuntimeError("CENSUS_API_KEY is not set")
    api_key = CENSUS_API_KEY
    # Define the base URL for the Census API
    year = int(answer[4])
    base_url = f"https://api.census.gov/data/{str(year)}/dec/pl"
    print(f"year: {year}")

    # Initialize census_data
    census_data = None

    if year == 2000:
        if answer[0] == "COUNTY":
            state_code = answer[1][:2]
            county_code = answer[1][2:]

            # Sample: https://api.census.gov/data/2000/dec/pl?get=NAME,PL001006&for=county:025&in=state:55&key=...
            params = {
                "get": "NAME," + answer[3],
                "for": f"county:{county_code}",
                "in": f"state:{state_code}",
                "key": api_key,
            }

            response = requests.get(base_url, params=params)

            # Check if the request was successful
            if response.status_code == 200:
                census_data = response.json()
                #print(f"Census API response: {census_data}")
            else:
                raise Exception(f"Census API Error: {response.status_code}")

        elif answer[0] == "STATE":
            params = {
                "get": "NAME," + answer[3],
                "for": f"state:{answer[1]}",
                "key": api_key,
            }

            response = requests.get(base_url, params=params)

            # Check if the request was successful
            if response.status_code == 200:
                census_data = response.json()
                print(f"Census API response: {census_data}")

    elif year == 2010:
        # sample: https://api.census.gov/data/2010/dec/sf1?get=NAME,P001001&for=county:025&in=state:55&key=REDACTED_CENSUS_KEY
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

            # Check if the request was successful
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

            # Check if the request was successful
            if response.status_code == 200:
                census_data = response.json()
                print(f"Census API response: {census_data}")

    elif year == 2020:
        # example: https://api.census.gov/data/2020/dec/pl?get=P1_001N&for=county:025&in=state:55
        print("ran 2020")
        print(answer)
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
            

            # Check if the request was successful
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

            # Check if the request was successful
            if response.status_code == 200:
                census_data = response.json()
                print(f"Census API response: {census_data}")
        


    if census_data is None:
        census_data = {"error": "No Census data retrieved"}

    # Second ChatGPT request, using `census_data`
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": f"""Use the following information, and only the following information to answer the message.
                Here is the information: {census_data}"""},
            {"role": "user", "content": f"message: {prompt}, csv: {csv_text}"}
        ],
        max_tokens=200,
        temperature=0.1
    )

    final_response = response.choices[0].message.content
    return final_response

    



if __name__ == "__main__":
    app.run(port=5002)
