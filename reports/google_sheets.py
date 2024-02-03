from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


def upload_to_google_sheet(file_name):
    # Set the path to your Excel file
    # excel_file_path = 'HOURLY.xlsx'

    # Set the service account email
    # service_account_email = 'hourly-data-generator@asklepiydfs.iam.gserviceaccount.com'

    # Set the destination folder ID in Google Drive
    drive_folder_id = '1ZGc4P3BRbWr7iMcoINsTMq6LsCf9LgLI'

    # Set up service account credentials
    credentials = Credentials.from_service_account_file('reports/credentials.json',
                                                        scopes=['https://www.googleapis.com/auth/drive.file'])

    # Create Google Drive service
    drive_service = build('drive', 'v3', credentials=credentials)

    # Upload the Excel file to Google Drive
    file_metadata = {'name': file_name, 'parents': [drive_folder_id]}
    media = MediaFileUpload(file_name,
                            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    uploaded_file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()

    print(f'File uploaded to Google Drive with ID: {uploaded_file["id"]} with name {file_name}')
