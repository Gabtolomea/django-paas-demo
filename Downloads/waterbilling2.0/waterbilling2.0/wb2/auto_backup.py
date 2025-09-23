import os
import datetime
import subprocess
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle

# === DATABASE CONFIG ===
DB_NAME = "wb2"
DB_USER = "root"
DB_PASSWORD = "jazfer"
DB_HOST = "localhost"
DB_PORT = "3307"

# === LOCAL BACKUP DIRECTORY ===
# BACKUP_DIR = os.path.join(os.getcwd(), "backups")
# os.makedirs(BACKUP_DIR, exist_ok=True)
BACKUP_DIR = r"C:\db_backups"
os.makedirs(BACKUP_DIR, exist_ok=True)


# === GOOGLE DRIVE CONFIG ===
FOLDER_ID = "1JAOSsaZ0Hbh9lapN2IZzrbguxztCrnzh"  # Your Drive folder ID
SCOPES = ['https://www.googleapis.com/auth/drive.file']

def backup_database():
    """Dump database to a .sql file locally"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"backup_{timestamp}.sql"
    filepath = os.path.join(BACKUP_DIR, filename)

    dump_cmd = [
    r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqldump.exe",
    f"--user={DB_USER}",
    f"--password={DB_PASSWORD}",
    f"--host={DB_HOST}",
    f"--port={DB_PORT}",
    "--column-statistics=0",
    DB_NAME,
]


    with open(filepath, "w", encoding="utf-8") as f:
        subprocess.run(dump_cmd, stdout=f, check=True)

    print(f"✅ Local backup created: {filepath}")
    return filepath

def authenticate_drive():
    """Authenticate with Google Drive API"""
    creds = None
    if os.path.exists("token.pkl"):
        with open("token.pkl", "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.pkl", "wb") as token:
            pickle.dump(creds, token)

    service = build("drive", "v3", credentials=creds)
    return service

def upload_to_drive(filepath):
    """Upload a file to Google Drive"""
    service = authenticate_drive()
    file_metadata = {
        "name": os.path.basename(filepath),
        "parents": [FOLDER_ID]
    }
    media = MediaFileUpload(filepath, resumable=True)
    file = service.files().create(body=file_metadata, media_body=media, fields="id").execute()
    print(f"☁️ Backup uploaded to Drive with ID: {file.get('id')}")

if __name__ == "__main__":
    sql_file = backup_database()
    upload_to_drive(sql_file)
