# Import necessary libraries
import os
import time
from datetime import datetime  # For working with dates

import pandas as pd  # For working with DataFrames
from dotenv import load_dotenv
from sqlalchemy import create_engine  # For creating a connection engine

from reports.formatter import formatter
from reports.inn_for_oxvat import excluded_clients


def oxvat_generator():
    print('Started running oxvat_generator')
    oxvated_clients = excluded_clients()
    start_time = time.time()

    # Load environment variables from the file
    env_file_path = 'D:/Projects/.env'
    load_dotenv(env_file_path)

    # Get today's date
    today_date = datetime.now().strftime('%d %b')
    output_file_path = f'NE OXVACHEN - {today_date}.xlsx'
    promotion_path = "D:\Projects\promotion.xlsx"

    # Load data from different sheets in 'promotion.xlsx' into DataFrames
    region_df = pd.read_excel(promotion_path, sheet_name='Region')
    problem_clients = pd.read_excel(promotion_path, sheet_name='problemClients')
    problem_clients['INN'] = problem_clients['INN'].astype(int)

    # Access the environment variables
    db_server = os.getenv("DB_SERVER")
    db_database = os.getenv("DB_DATABASE_ASKGLOBAL")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_port = os.getenv("DB_PORT")
    db_driver_name = os.getenv("DB_DRIVER_NAME")

    # Construct the connection string
    conn_str = (f"mssql+pyodbc://{db_user}:{db_password}@{db_server}:{db_port}/{db_database}?driver={db_driver_name}")

    engine = create_engine(conn_str)

    procedure_name = "atCalcExtraLimitsByInn"
    # Build the SQL query with parameterized query
    sql_query = f""" EXEC {procedure_name} """

    # 💀💀💀 EXECUTION!!! ⚠️⚠️⚠️
    df = pd.read_sql_query(sql_query, engine)

    df.drop_duplicates(subset=['ИНН клиента'], inplace=True)

    # Create a temporary column for comparison without changing the original data type
    df['ИНН клиента_temp'] = pd.to_numeric(df['ИНН клиента'], errors='coerce')

    # Perform the comparison
    df = df[~df['ИНН клиента_temp'].isin(problem_clients['INN'])]
    df = df[~df['ИНН клиента_temp'].isin(oxvated_clients['INN'])]
    # df = df[~df['ИНН клиента_temp'].isin(problem_clients['INN'].tolist() + oxvated_clients['INN'].tolist())]

    # Drop the temporary column
    df = df.drop(columns=['ИНН клиента_temp'])

    df['Manager'] = df['Менеджер/ка'].str.strip()
    # Merge with 'region_df' DataFrame based on 'ClientMan'
    df = pd.merge(df, region_df[['ClientMan', 'Region']], left_on='Manager', right_on='ClientMan', how='left')

    df = df[['Филиал', 'Region', 'Manager', 'ИНН клиента', 'Наименование клиента', 'Лимит клиента', 'Дебиторка',
             'Свободный лимит']]
    df = df[df['Свободный лимит'] > 10_000]
    df.sort_values(by=['Region', 'Manager'], inplace=True)

    df.to_excel(output_file_path, index=False)
    # Load the existing workbook

    formatter(df, output_file_path)
