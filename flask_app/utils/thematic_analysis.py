import os
from openai import OpenAI
import json

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def perform_thematic_analysis(entries):
    prompt = "Analyze the following journal entries and provide a comprehensive thematic analysis. Include main themes, emotions, patterns, and a summary. Format the response as a JSON object with keys: main_themes (list), emotions (list), patterns (list), and summary (string).\n\n"
    for entry in entries:
        prompt += f"Content: {entry['content']}\n"

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a sophisticated qualitative researcher. Provide an in-depth thematic analysis of journal entries, highlighting main themes, emotions, and patterns with clarity."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=2000
    )

    # Parse the JSON response
    analysis_result = json.loads(response.choices[0].message.content)
    return analysis_result
