import requests


def send_customer_payment(customer_email, payment_token):
    body = {"email": customer_email, "payment": payment_token}
    return requests.post("https://payments.example.invalid/collect", json=body)
