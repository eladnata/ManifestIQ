import requests


def run():
    password = "example"
    print("password", password)
    return requests.get("https://internal.example/api")
