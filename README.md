# DotAsset

DotAsset is an early-stage backend prototype we built while exploring an idea around using LLMs to help analyze public data for investment research. The original goal was to make it easier to pull structured information from sources like the US Census and combine it with natural-language queries.

This repo shows the groundwork: API integrations, data handling, and how an LLM can be used as a decision layer within the pipeline.

---

## What this project does

At a high level:

- Exposes a small Flask API endpoint
- Accepts a natural-language query
- Uses GPT to select relevant Census variables and geography
- Fetches the corresponding Census data
- Uses GPT again to help interpret the result

The core idea was to let the model reason about *what data to fetch*, then let deterministic APIs return the actual numbers.

---

## How it works

1. A request is sent to the Flask server with a user question.
2. The first GPT call is constrained to return a structured tuple:
   - Geography
   - FIPS code
   - Census variable
   - Year
3. The backend uses that output to construct a Census API request.
4. The raw Census response is passed into a second GPT call to generate a human-readable answer.

All API keys are loaded through environment variables.

---

## Tech stack

- Python
- Flask
- OpenAI API
- US Census API
- Pandas (for CSV-based variable lookup)

---

## Why this exists

This repo is not meant to be a polished startup demo.

It exists to show:
- How to safely integrate LLMs with real data sources
- How to constrain model output for downstream automation
- How to structure a backend that mixes probabilistic and deterministic systems

We stopped development early, but the architectural direction is intentional.

---

## Running locally

1. Copy the example env file:
   ```
   cp .env.example .env
   ```

2. Add your API keys to `.env`

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Start the server:
   ```
   python CensusDemo.py
   ```

---

## Notes

If this plan is continued, the next steps would be better validation, error handling, and a cleaner request/response contract.
