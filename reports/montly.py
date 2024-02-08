import os
from datetime import datetime  # For working with dates

import pandas as pd  # For working with DataFrames
from dotenv import load_dotenv
from sqlalchemy import create_engine  # For creating a connection engine

from reports.formatter import formatter


def monthly_generator():
    ##################### LOADING IMPORTANT DATA ######################
    print('Started running monthly generator')
    # Load environment variables from the .env file

    env_file_path = 'D:/Projects/.env'
    load_dotenv(env_file_path)

    output_file_path = 'MONTHLY.xlsx'
    # Load data from different sheets in 'promotion.xlsx' into DataFrames
    promotion_path = 'D:\Projects\promotion.xlsx'
    region_df = pd.read_excel(promotion_path, sheet_name='Region')
    aksiya_df = pd.read_excel(promotion_path, sheet_name='Aksiya')
    paket_df = pd.read_excel(promotion_path, sheet_name='Paket')
    types_df = pd.read_excel(promotion_path, sheet_name='TYPES')
    ##################### ACCESS ENV VARIABLES ######################

    db_server = os.getenv("DB_SERVER")
    db_database = os.getenv("DB_DATABASE_ASKGLOBAL")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_port = os.getenv("DB_PORT")
    db_driver_name = os.getenv("DB_DRIVER_NAME")

    ##################### PROCEDURE NAME ######################
    procedure_name = os.getenv("MONTHLY")  # THIS IS HOURLY DATA GATHERING

    # Set default values for date_begin and date_end if not provided
    date_begin = datetime(2024, 2, 1).strftime('%Y%m%d')
    date_end = datetime(2024, 3, 31).strftime('%Y%m%d')
    CURRENT_MONTH = 2
    CURRENT_YEAR = 2024
    ##################### CONNECTION STRING AND SQL QUERY ######################
    # Construct the connection string
    conn_str = f"mssql+pyodbc://{db_user}:{db_password}@{db_server}:{db_port}/{db_database}?driver={db_driver_name}"
    engine = create_engine(conn_str)

    sql_query = f"""
    DECLARE @DateBegin DATE = ?;
    DECLARE @DateEnd DATE = ?;
    
    EXEC {procedure_name}
        @DataBegin = @DateBegin,
        @DataEnd = @DateEnd;
    """

    #####################  EXECUTION  ######################
    df = pd.read_sql_query(sql_query, engine, params=(date_begin, date_end))

    ##################### BASIC FILTER ######################
    df['DataEntered'] = pd.to_datetime(df['DataEntered'])
    df = df[(df['DataEntered'].dt.year >= CURRENT_YEAR) & df['DocName'].isin(
        ['Оптовая реализация', 'Финансовая скидка', 'Возврат товара от покупателя'])]
    df.rename(columns={'GoodId': 'Goodid', 'ClientManager': 'ClientMan', 'INN': 'inn'}, inplace=True)
    region_df['ClientMan'] = region_df['ClientMan'].str.title()
    df['ClientMan'] = df['ClientMan'].str.title()
    df = pd.merge(df, region_df[['ClientMan', 'Region']], left_on='ClientMan', right_on='ClientMan', how='left')
    df = pd.merge(df, aksiya_df[['Goodid', 'Aksiya']], left_on='Goodid', right_on='Goodid', how='left')
    df = pd.merge(df, paket_df[['Goodid', 'Paket']], left_on='Goodid', right_on='Goodid', how='left')

    df['OXVAT'] = df['inn'].map(df['inn'].value_counts())
    df['inn_temp'] = pd.to_numeric(df['inn'], errors='coerce')
    types_df['INN_temp'] = pd.to_numeric(types_df['INN'], errors='coerce')
    df = pd.merge(df, types_df[['INN_temp', 'TYPE', 'RegionType']], left_on='inn_temp', right_on='INN_temp', how='left')
    df['TYPE'].fillna('ROZ', inplace=True)
    df.loc[df['TYPE'] == 'ROZ', 'RegionType'] = df['Region']
    df.drop(['INN_temp', 'inn_temp'], axis=1, inplace=True)

    categorical_columns = ['Office', 'DocName', 'YY', 'MM', 'Goodid', 'Good', 'Producer', 'Client', 'inn', 'City',
                           'ClientType', 'InvoiceManager', 'ClientMan', 'Store', 'StoreDep', 'DownPayment',
                           'PaymentTerm', 'FSkidka', 'InClient', 'BaseMarkUp', 'Postavshik', 'Region', 'Aksiya',
                           'Paket', 'TYPE', 'RegionType']
    df[categorical_columns] = df[categorical_columns].astype('category')

    df.to_excel(output_file_path, index=False)
    formatter(df, output_file_path)
