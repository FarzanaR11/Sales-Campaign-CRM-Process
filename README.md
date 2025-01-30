# Sales-Campaign-CRM-Process
Sales Campaign CRM Process with automation using Python and relevant APIs.

Sales-Campaign-CRM/
│── supervisor_agent/
│   ├── monitor.py   # Script to check for new leads and assign tasks
│   ├── assign_tasks.py  # Distributes tasks to Agent A & B
│── agent_a/
│   ├── verify_leads.py   # Email validation using Hunter.io/NeverBounce
│── agent_b/
│   ├── send_campaign.py  # Email outreach via SendGrid/AWS SES
│   ├── update_response.py  # Captures lead responses
│── utils/
│   ├── google_sheets.py  # Google Sheets API integration
│   ├── email_handler.py  # Gmail API for monitoring emails
│── config.py  # API keys & environment settings
│── requirements.txt  # Dependencies
│── README.md  # Documentation
│── main.py  # Entry point to run the automation
