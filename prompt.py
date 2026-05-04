import google.generativeai as genai
import os

def generate_response(prompt):
    # initialize the model
    model = genai.GenerativeModel("gemini-2.0-pro")

    # generate a response
    response = model.generate_content(prompt)

    return response.text

prompt = "You are a stock anlayzer and investment advisor. What are the top 5 stocks to invest in right now and why?"
response = generate_response(prompt)
print(response)