from google import genai
import os

def generate_response(prompt):
    # initialize the model
    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

    # The new way to generate content
    response = client.models.generate_content(
        model="gemini-2.0-pro", 
        contents=prompt
    )

    return response.text

prompt = "You are a stock anlayzer and investment advisor. What are the top 5 stocks to invest in right now and why?"
response = generate_response(prompt)
print(response)