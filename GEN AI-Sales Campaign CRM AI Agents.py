# -*- coding: utf-8 -*-
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import smtplib
import imaplib
import email
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from apscheduler.schedulers.blocking import BlockingScheduler
import requests

# Step 1: Setup Input Handling - Google Sheets Authentication
SCOPE = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
CREDENTIALS_FILE = "crendentials.json"  # JSON credentials file - Google Sheets API for automation and updates
SPREADSHEET_NAME = "Sales Campaign CRM"  # Spreadsheet name

creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, SCOPE)
client = gspread.authorize(creds)
sheet = client.open(SPREADSHEET_NAME).sheet1  # Access first sheet

# Email Configuration
SMTP_SERVER = "smtp.sender.com"
SMTP_PORT = 587
EMAIL_USER = "sender@agent.com"  # email
EMAIL_PASSWORD = "password"  # password
IMAP_SERVER = "imap.gmail.com"

# NeverBounce API for real-time email validation
NEVERBOUNCE_API_KEY = "API KEY"

# Custom Python scripts - Regex for basic syntax email validation
def is_valid_email(email):
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(pattern, email)

# Step 3: Agent A Task - Verifies lead email using NeverBounce API
def agent_a_verify_leads():
    data = sheet.get_all_records()
    for index, row in enumerate(data, start=2):  # Skip headers
        if row["Email Verified"] == "":
            email = row["Email"]
            if is_valid_email(email):
                response = requests.get(f"https://api.neverbounce.com/v4/single/check?key={NEVERBOUNCE_API_KEY}&email={email}")
                result = response.json()
                if result["result"] == "valid":
                    sheet.update_acell(f'F{index}', 'Y')
                else:
                    sheet.update_acell(f'F{index}', 'N')

# Step 4: Agent B Task - Sends campaign email : custom scripts for sending emails
def agent_b_send_email():
    data = sheet.get_all_records()
    for index, row in enumerate(data, start=2):
        if row["Email Verified"] == "Y" and row["Response Status"] == "":
            recipient = row["Email"]
            subject = "Exclusive Offer: Join Our Platform"
            message_body = f"""
            Dear {row["Lead Name"]},

            We would love to invite you to check out our services. Let us know your interest!

            Best Regards,
            Sales Team
            """

            try:
                msg = MIMEMultipart()
                msg["From"] = EMAIL_USER
                msg["To"] = recipient
                msg["Subject"] = subject
                msg.attach(MIMEText(message_body, "plain"))

                server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
                server.starttls()
                server.login(EMAIL_USER, EMAIL_PASSWORD)
                server.sendmail(EMAIL_USER, recipient, msg.as_string())
                server.quit()

                sheet.update_acell(f'G{index}', "Sent")
            except Exception as e:
                sheet.update_acell(f'G{index}', f"Failed: {str(e)}")

# Step 2: Supervisor Agent Task - Monitors email for tasks
def monitor_email():
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL_USER, EMAIL_PASSWORD)
    mail.select("inbox")

    _, search_data = mail.search(None, "UNSEEN")
    for num in search_data[0].split():
        _, msg_data = mail.fetch(num, "(RFC822)")
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                subject = msg["subject"]
                if "New Sales Campaign Task" in subject:
                    sheet.update_acell('H1', 'New Task Detected')
    mail.logout()

# Step 5: Supervisor Agent Output - Summarizes progress
def supervisor_summary():
    data = sheet.get_all_records()
    total_leads = len(data)
    verified_leads = sum(1 for row in data if row["Email Verified"] == "Y")
    interested_leads = sum(1 for row in data if row["Response Status"] == "Interested")

    summary = f"Total Leads: {total_leads}\nVerified: {verified_leads}\nInterested: {interested_leads}"
    sheet.update_acell('H2', summary)

    msg = MIMEMultipart()
    msg["From"] = EMAIL_USER
    msg["To"] = "stakeholder@recipient.com"  # recipient
    msg["Subject"] = "Sales Campaign Summary"
    msg.attach(MIMEText(summary, "plain"))

    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(EMAIL_USER, EMAIL_PASSWORD)
    server.sendmail(EMAIL_USER, "farzanarahmanrima2014@gmail.com", msg.as_string())
    server.quit()

# Scheduler function to manage tasks - Task Automation: Python with apscheduler for regular checks
def scheduled_tasks():
    print("Starting to monitor email...")
    monitor_email()
    print("Finished email monitoring.")

    print("Starting lead verification...")
    agent_a_verify_leads()
    print("Lead verification done.")

    print("Starting email campaign...")
    agent_b_send_email()
    print("Email campaign done.")

    print("Starting supervisor summary...")
    supervisor_summary()
    print("Supervisor summary done.")

if __name__ == "__main__":
    scheduler = BlockingScheduler()

    # Add jobs to the scheduler
    scheduler.add_job(scheduled_tasks, 'interval', minutes=5)

    # Run the scheduler
    scheduler.start()

"""Debugging and Testing"""

# Get data outside the function to make it accessible globally
client = authenticate_google_sheets()
sheet = client.open("Sales Campaign CRM").sheet1
data = sheet.get_all_records()  # Get data here

print(data[0])  # This will print the first row (which should be the header)

import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_name(
    "credentials.json", scope
)

try:
    client = gspread.authorize(creds)
    print("Authentication successful!")
except Exception as e:
    print("Error:", e)

for index, row in enumerate(data, start=2):
    if not row:  # Skip any empty rows
        continue

    # Strip any extra spaces in the column names
    row = {key.strip(): value for key, value in row.items()}

    if row["Email Verified"] == "Y" and row["Response Status"] == "":
        recipient = row["Email"]
        if not is_valid_email(recipient) or not verify_email_with_neverbounce(recipient):
            sheet.update_acell(f'G{index}', "Failed: Invalid Email")
            continue
