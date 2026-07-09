import requests


def call_provider(prompt_text):
    payload = {"model": "gpt-4.1", "prompt": prompt_text, "max_tokens": 128}
    return requests.post("https://api.openai.com/v1/chat/completions", json=payload)
