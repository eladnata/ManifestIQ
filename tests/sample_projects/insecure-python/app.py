import os
import sqlite3
import subprocess
import hashlib

DEBUG = True
API_KEY = "AKIA1234567890ABCDEF"
DB_PASSWORD = "SuperSecret123"


def run_report(user_input):
    subprocess.run("ls " + user_input, shell=True)


def get_invoice(invoice_id):
    conn = sqlite3.connect("finance.db")
    query = f"select * from invoices where id = {invoice_id}"
    return conn.execute(query).fetchall()


def hash_customer_id(customer_id):
    return hashlib.md5(customer_id.encode()).hexdigest()
