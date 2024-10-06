import os
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def perform_thematic_analysis(entries):
    prompt = "Meticulously analyze the journal entries and provide a comprehensive summary of the main themes, emotions, and patterns:\n\n"
    for entry in entries:
        prompt += f"Content:\n- Detailed Observation: {entry['detailed_observation']}\n- Reflection: {entry['reflection']}\n"

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "As a sophisticated qualitative researcher, provide in-depth thematic analysis of journal entries, highlighting main themes, emotions, and patterns with clarity."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=2000
    )

    return response.choices[0].message.content
