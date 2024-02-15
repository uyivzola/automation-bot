import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

drive_folder_id = '1ZGc4P3BRbWr7iMcoINsTMq6LsCf9LgLI'
user_emails = ['Behzod.Hidirov@asklepiygroup.uz', 'behzodxidirov@gmail.com']
# Set up service account credentials
credentials = Credentials.from_service_account_file('reports/credentials.json',
                                                    scopes=['https://www.googleapis.com/auth/drive.file'])
# Create Google Drive service
drive_service = build('drive', 'v3', credentials=credentials)


def upload_to_google_sheet(file_name):
    # Set the path to your Excel file
    # excel_file_path = 'HOURLY.xlsx'

    # Set the service account email
    # service_account_email = 'hourly-data-generator@asklepiydfs.iam.gserviceaccount.com'

    # Set the destination folder ID in Google Drive

    # Upload the Excel file to Google Drive
    file_metadata = {'name': file_name, 'parents': [drive_folder_id]}
    media = MediaFileUpload(file_name, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    uploaded_file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()

    print(f'File uploaded to Google Drive with ID: {uploaded_file["id"]} with name {file_name}')


def create_google_sheet(credential, title, folder_id):
    drive_services = build('drive', 'v3', credentials=credential)
    file_metadata = {'name': title, 'parents': [folder_id], 'mimeType': 'application/vnd.google-apps.spreadsheet'}
    spreadsheet = drive_services.files().create(body=file_metadata, fields='id').execute()
    print(spreadsheet)
    return spreadsheet


def give_permissions(sheet_id, user_email):

    for email in user_email:
        user_permission = {'type': 'user', 'role': 'writer', 'emailAddress': email}
        drive_service.permissions().create(fileId=sheet_id, body=user_permission).execute()


def write_df_to_google_sheet(df, file_name, sheet_name='Sheet1'):
    # Authorize gspread with the same credentials
    gc = gspread.authorize(credentials)

    try:
        # Try to open the existing Google Sheets spreadsheet
        spreadsheet = gc.open(file_name)
        # Get the existing or create a new worksheet by name
        worksheet = spreadsheet.worksheet(sheet_name)

    except gspread.SpreadsheetNotFound:
        # If the spreadsheet doesn't exist, create a new one in the specified folder
        spreadsheet = create_google_sheet(credentials, file_name, drive_folder_id)
        worksheet = spreadsheet.add_worksheet(title=sheet_name, rows=df.shape[0], cols=df.shape[1])
        sheet_id = spreadsheet.id
        give_permissions(sheet_id, user_emails)

    # Write the DataFrame to the Google Sheets sheet
    worksheet.update([df.columns.values.tolist()] + df.values.tolist())

    print(f'DataFrame exported to Google Sheets: {spreadsheet.url}')
