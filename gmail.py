from __future__ import print_function
from base64 import urlsafe_b64encode
from email.mime.text import MIMEText

import sys
import logging
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import utils


# https://www.thepythoncode.com/article/sending-emails-in-python-smtplib

# https://developers.google.com/gmail/api/quickstart/python
# https://www.thepythoncode.com/article/use-gmail-api-in-python
def authenticate():
    # https://developers.google.com/identity/protocols/oauth2/scopes#gmail
    # If modifying these scopes, delete the file token.json.
    SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

    gmail_credentials_file = 'gmail-credentials.json'
    gmail_token_file = 'gmail-token.json'
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(gmail_token_file):
        creds = Credentials.from_authorized_user_file(gmail_token_file, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                gmail_credentials_file, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(gmail_token_file, 'w') as token:
            token.write(creds.to_json())

    service = None

    try:
        # Call the Gmail API
        service = build('gmail', 'v1', credentials=creds)
    except HttpError as error:
        logging.error(f'An error occurred: {error}')
    
    return service


def send_email(service, to, subject, body):
    our_email = 'campbell@yogasix.com'

    message = MIMEText(body)
    message['bcc'] = to
    message['from'] = our_email
    message['subject'] = subject
    
    msg = {'raw': urlsafe_b64encode(message.as_bytes()).decode()}

    return service.users().messages().send(
      userId="me",
      body=msg
    ).execute()


def read_email_from_file(filename):
    file = open(filename, mode='r')
    txt = file.read()
    file.close()
    return txt


def email_members():
    email_batch_size = 20
    utils.config_logging()
    service = authenticate()

    subject = 'Y6 Campbell: Special Offer On Class Packs!'
    body = read_email_from_file('gmail-template.txt')
    logging.info(f"Sending email using subject: {subject} body {body}")

    df = utils.read_members_xlsx(xlsx)
    df = df["Email"]

    i = 0
    while i <= len(df):
        email_ids = ",".join(df[i:i+email_batch_size].values.flatten().tolist())
        logging.info(f"Sending email to list [{email_ids}]")
        status = send_email(service, email_ids, subject, body)
        logging.info(f"Email status: {status}")
        i += email_batch_size

    # status = send_email(service, "kumar.soumitra@gmail.com,ajnavi.kumar@yogasix.com", subject, body)
    # logging.info(f"Email status: {status}")


if __name__ == '__main__':
    # Send email to members in the "Email" column of the input XLSX file
    xlsx = sys.argv[1] if len(sys.argv) > 1 else "LeadsExport.xlsx" 
    email_members()
