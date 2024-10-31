from openai import OpenAI
from typing import Dict, Any, List
from webreader.prompts import WEBSITE_SUMMARY_PROMPT
import json



def get_gpt_response(chat_history: List[Dict[str, Any]]) -> str:
    client = OpenAI()

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=chat_history,
        temperature=0.5,
        stream=True,
    )
    return response

def get_website_summary(formatted_website_data: str) -> str:
    client = OpenAI()

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": WEBSITE_SUMMARY_PROMPT}, 
            {"role": "user", "content": formatted_website_data}
        ],
        temperature=0.5,
        stream=True,
    )
    return response



if __name__ == "__main__":
    pass