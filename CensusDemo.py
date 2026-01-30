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

if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY is not set")
client = OpenAI(api_key=OPENAI_API_KEY)

if not CENSUS_API_KEY:
    raise RuntimeError("CENSUS_API_KEY is not set")

YEAR_TO_DATASET = {
    2000: "dec/pl",
    2010: "dec/sf1",
    2020: "dec/pl",
}

def parse_gpt_tuple(raw: str):
    s = raw.strip()

    if s.startswith("(") and s.endswith(")"):
        s = s[1:-1].strip()

    raw_parts = s.split(",")

    parts = []
    for part in raw_parts:
        cleaned = part.strip()
        cleaned = cleaned.strip("'")
        cleaned = cleaned.strip('"')
        parts.append(cleaned)

    if len(parts) != 5:
        raise ValueError(f"Unexpected GPT format. Got {len(parts)} fields: {parts}")

    geography = parts[0]
    fips = parts[1]
    var_desc = parts[2]
    var_label = parts[3]
    year = int(parts[4])

    return geography, fips, var_desc, var_label, year


def build_census_request(year: int, geography: str, fips: str, var_label: str):
    #returns url and params for census api request
    dataset = YEAR_TO_DATASET.get(year)
    if not dataset:
        raise ValueError(f"Unsupported year: {year}")

    base_url = f"https://api.census.gov/data/{year}/{dataset}"

    include_name = year in (2000, 2010)

    if include_name:
        get_value = f"NAME,{var_label}"
    else:
        get_value = var_label

    params = {"get": get_value, "key": CENSUS_API_KEY}

    geography = geography.upper().strip()

    if geography == "COUNTY":
        # fips is like "55025" => state 55, county 025
        if len(fips) < 5:
            raise ValueError(f"COUNTY fips should look like SSCCC (e.g. 55025). Got: {fips}")

        state_code = fips[:2]
        county_code = fips[2:]

        params["for"] = f"county:{county_code}"
        params["in"] = f"state:{state_code}"

    elif geography == "STATE":
        params["for"] = f"state:{fips}"

    else:
        raise ValueError(f"Unsupported geography: {geography}")

    return base_url, params


def fetch_census_json(url: str, params: dict):
    resp = requests.get(url, params=params, timeout=15)
    if resp.status_code != 200:
        raise Exception(f"Census API Error: {resp.status_code} - {resp.text[:200]}")
    return resp.json()

def get_answer(prompt: str):
    #Ask GPT to select geography/variable/year
    first = client.chat.completions.create(
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

    raw_answer = first.choices[0].message.content
    geography, fips, var_desc, var_label, year = parse_gpt_tuple(raw_answer)

    print(f"GPT picked: geography={geography}, fips={fips}, var={var_label}, year={year}")

    #Fetch Census data
    census_data = None
    try:
        url, params = build_census_request(year, geography, fips, var_label)
        census_data = fetch_census_json(url, params)
        print(f"Census API response: {census_data}")
    except Exception as e:
        census_data = {"error": str(e), "year": year, "geography": geography, "fips": fips, "variable": var_label}

    #Ask GPT to answer feeding only census data as information bank
    second = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": f"""Use the following information, and only the following information to answer the message.
Here is the information: {census_data}"""},
            {"role": "user", "content": f"message: {prompt}, csv: {csv_text}"}
        ],
        max_tokens=200,
        temperature=0.1
    )

    return second.choices[0].message.content


@app.route('/process', methods=['POST'])
def process_data():
    data = request.get_json()

    if "message" in data:
        processed_message = get_answer(data["message"])
        return jsonify({
            "originalMessage": data["message"],
            "processedMessage": processed_message,
        })

    return jsonify({"error": "Missing 'message' key"}), 400


if __name__ == "__main__":
    app.run(port=5002)
