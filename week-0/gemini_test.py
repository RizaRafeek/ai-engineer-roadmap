import os
from google import genai

def ask_gemini(prompt: str) -> str:
    client = genai.Client(api_key = os.environ.get("GEMINI_API_KEY"))

    interaction = client.models.generate_content(
        model = "gemini-2.5-flash" ,
        contents = prompt
    )
    return interaction.text

if __name__ == '__main__':
    print(ask_gemini("Where are you"))