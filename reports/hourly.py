import os
from datetime import datetime, timedelta  # For working with dates

import pandas as pd  # For working with DataFrames
from dotenv import load_dotenv
from sqlalchemy import create_engine  # For creating a connection engine

from reports.formatter import formatter
from reports.google_sheets import upload_to_google_sheet


def hourly_generator():
    ##################### LOADING IMPORTANT DATA ######################
    # Load environment variables from the .env file
    env_file_path = 'D:/Projects/.env'
    load_dotenv(env_file_path)
    # Giving output file name
    output_file_path = 'HOURLY.xlsx'
    # Load data from different sheets in 'promotion.xlsx' into DataFrames
    promotion_path = r'D:\Projects\promotion.xlsx'
    region_df = pd.read_excel(promotion_path, sheet_name='Region')
    aksiya_df = pd.read_excel(promotion_path, sheet_name='Aksiya')
    paket_df = pd.read_excel(promotion_path, sheet_name='Paket')
    types_df = pd.read_excel(promotion_path, sheet_name='TYPES')

    ##################### ACCESS ENV VARIABLES ######################
    db_server = os.getenv("DB_SERVER")
    db_database = os.getenv("DB_DATABASE_SERGELI")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_port = os.getenv("DB_PORT")
    db_driver_name = os.getenv("DB_DRIVER_NAME")

    ##################### PROCEDURE NAME ######################
    procedure_name = os.getenv("HOURLY_SHORT")  # THIS IS HOURLY DATA GATHERING

    ##################### DATE - JANUARY ######################
    CURRENT_MONTH = 1
    CURRENT_YEAR = 2024
    today_date = datetime.now().strftime('%d/%m/%Y')
    tomorrow_date = (datetime.now() + timedelta(days=1)).strftime('%d/%m/%Y')

    ##################### CONNECTION STRING AND SQL QUERY ######################
    # Construct the connection string
    conn_str = f"mssql+pyodbc://{db_user}:{db_password}@{db_server}:{db_port}/{db_database}?driver={db_driver_name}"
    engine = create_engine(conn_str)

    sql_query = f"""
        DECLARE @DateBegin DATE = ?;
        DECLARE @DateEnd DATE = ?;

        EXEC {procedure_name}
            @DateBegin = @DateBegin,
            @DateEnd = @DateBegin;
    """

    #####################  EXECUTION  ######################
    df = pd.read_sql_query(sql_query, engine, params=(today_date, tomorrow_date))

    ##################### BASIC FILTER ######################
    df['DataEntered'] = pd.to_datetime(df['DataEntered'])
    df = df[(df['DataEntered'].dt.month == CURRENT_MONTH) & (df['DataEntered'].dt.year == CURRENT_YEAR) & (
            df['DataEntered'].dt.date == datetime.now().date()) & df['Dname'].isin(
        ['Оптовая реализация', 'Финансовая скидка'])]

    df['B.Summ'] = df['BasePrice'] * df['Kolich']
    df['TotalAmount'] = df['oPrice'] * df['Kolich']

    region_df['ClientMan'] = region_df['ClientMan'].str.title()
    df['ClientMan'] = df['ClientMan'].str.title()

    df = pd.merge(df, aksiya_df[['Goodid', 'Aksiya']], left_on='Goodid', right_on='Goodid', how='left')
    df = pd.merge(df, paket_df[['Goodid', 'Paket']], left_on='Goodid', right_on='Goodid', how='left')
    df = pd.merge(df, region_df[['ClientMan', 'Region']], left_on='ClientMan', right_on='ClientMan', how='left')

    df['OXVAT'] = df['inn'].map(df['inn'].value_counts())

    df['inn_temp'] = pd.to_numeric(df['inn'], errors='coerce')
    types_df['INN_temp'] = pd.to_numeric(types_df['INN'], errors='coerce')
    df = pd.merge(df, types_df[['INN_temp', 'TYPE', 'RegionType']], left_on='inn_temp', right_on='INN_temp', how='left')

    ##################### ROZ | SET | OPT  ######################
    df['TYPE'].fillna('ROZ', inplace=True)
    df.loc[df['TYPE'] == 'ROZ', 'RegionType'] = df['Region']
    df.drop(['INN_temp', 'inn_temp'], axis=1, inplace=True)
    df.columns = ['Office', 'IncData', 'Number', 'Dname', 'ExpData', 'SerialNo', 'Number', 'Month', 'Year', 'Data',
                  'Goodid', 'Good', 'Producer', 'Client', 'Vid', 'type', 'inn', 'City', 'SalerMan', 'ClientMan',
                  'Store', 'StoreDep', 'DownPayment', 'PaymentTerm', 'BasePrice', 'Price', 'oPrice', 'Kolich', 'MarkUp',
                  'rMarkUp', 'p25', 'p100', 'OrderID', 'DataEntered', 'gkm_group', 'B.Summ', 'TotalAmount', 'Aksiya',
                  'Paket', 'Region', 'OXVAT', 'TYPE', 'RegionType']

    ##################### CONVERT TO CATEGORICAL DATA TYPE ######################
    categorical_columns = ['TYPE', 'Region', 'Aksiya', 'Paket', 'ClientMan', 'Dname', 'Vid', 'City', 'type', 'Store',
                           'StoreDep', 'RegionType', 'Month', 'Year', 'Office', 'Producer']
    df[categorical_columns] = df[categorical_columns].astype('category')
    df.sort_values(by='DataEntered', ascending=False, inplace=True)
    df.to_excel(output_file_path, index=False)

    ##################### FORMAT THE TABLE  ######################
    formatter(df, output_file_path)
    ##################### MODIFIED TIME OF THE FILE ######################

    if os.path.exists(output_file_path):
        # Get the size of the file in bytes
        file_size_bytes = os.path.getsize(output_file_path)

        # Convert bytes to kilobytes, megabytes, or gigabytes for readability
        file_size_kb = file_size_bytes / 1024.0
        file_size_mb = file_size_kb / 1024.0
        file_size_gb = file_size_mb / 1024.0

        print(
            f"File Size: {file_size_bytes} bytes, {file_size_kb:.2f} KB, {file_size_mb:.2f} MB, {file_size_gb:.2f} GB")

        # Get the last modification time in seconds since the epoch
        modification_time_seconds = os.path.getmtime(output_file_path)

        # Convert seconds since the epoch to a datetime object
        modification_time = datetime.fromtimestamp(modification_time_seconds)

        # Get the change time (metadata change time) in seconds since the epoch
        change_time_seconds = os.path.getctime(output_file_path)

        # Convert seconds since the epoch to a datetime object
        change_time = datetime.fromtimestamp(change_time_seconds)

        print(f"Last Modified Time: {modification_time.strftime('%H:%M')}")
        print(f"Change Time: {change_time.strftime('%H:%M')}")

    else:
        print("File not found.")
