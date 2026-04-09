import os
import requests

BREVO_API_URL = 'https://api.brevo.com/v3/smtp/email'


def send_email(to_email: str, subject: str, html_content: str) -> bool:
    """Send an email using Brevo (Sendinblue) SMTP API."""
    api_key = os.environ.get('BREVO_API_KEY')
    sender_email = os.environ.get('SENDER_EMAIL')

    if not api_key or not sender_email:
        print('❌ BREVO_API_KEY or SENDER_EMAIL environment variable is missing.')
        return False

    payload = {
        'sender': {'email': sender_email},
        'to': [{'email': to_email}],
        'subject': subject,
        'htmlContent': html_content,
    }

    headers = {
        'accept': 'application/json',
        'content-type': 'application/json',
        'api-key': api_key,
    }

    try:
        response = requests.post(BREVO_API_URL, json=payload, headers=headers, timeout=15)
        print(f'Brevo status: {response.status_code}')
        print(f'Brevo response: {response.text}')
        return response.ok
    except Exception as exc:
        print(f'❌ Error sending email to {to_email}: {exc}')
        return False
