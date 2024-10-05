import openai
import os
from typing import List, Dict

openai.api_key = os.environ.get("OPENAI_API_KEY")

def perform_thematic_analysis(entries: List[Dict]) -> str:
    prompt = "Analyze the following journal entries and provide a summary of the main themes, emotions, and patterns:\n\n"
    for entry in entries:
        prompt += f"Title: {entry['title']}\n"
        prompt += f"Content: {entry['content']}\n"
        prompt += f"Date: {entry['date']}\n"
        prompt += f"Tags: {', '.join(entry['tags'])}\n\n"

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that analyzes journal entries and provides thematic analysis."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=500
    )

    return response.choices[0].message.content

