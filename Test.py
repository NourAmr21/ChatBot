import openai 
import json
import os
from dotenv import load_dotenv
from openai import OpenAI
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI()
#######################################################################################
with open(r"C:\Users\LENOVO\Downloads\scraped_data.json", "r", encoding="utf-8") as f:
    scraped = json.load(f)
#company_context = scraped[0]["text"].replace("\n", " ").strip()[:3000]
company_context = ""
for item in scraped:
    company_context += item["text"].replace("\n", " ").strip()[:] + " "
print(company_context[2000:2100])