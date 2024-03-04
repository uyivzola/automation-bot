# Import necessary libraries
import os
import time
from datetime import datetime  # For working with dates

import pandas as pd  # For working with DataFrames
from dotenv import load_dotenv
from sqlalchemy import create_engine  # For creating a connection engine

CURRENT_MONTH = 3
CURRENT_YEAR = 2024
START_DATE = 1
END_DATE = 31
END_MONTH = 12

env_file_path = 'D:/Projects/.env'


def excluded_clients():
    print('Generating Excluded Clients list')
    time1 = time.time()
    # Load environment variables from the .env file
    load_dotenv(env_file_path)
    # Get today's date
    bugun = datetime.now().date()

    # Access the environment variables
    db_server = os.getenv("DB_SERVER")
    db_database_askglobal = os.getenv("DB_DATABASE_ASKGLOBAL")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_port = os.getenv("DB_PORT")
    db_driver_name = os.getenv("DB_DRIVER_NAME")

    # Construct the connection string
    conn_str = (
        f"mssql+pyodbc://{db_user}:{db_password}@{db_server}:{db_port}/{db_database_askglobal}?driver={db_driver_name}")

    engine = create_engine(conn_str)
    procedure_name = "bGoodSaleWithInfo"

    # Set default values for date_begin and date_end if not provided
    date_begin = datetime(CURRENT_YEAR, CURRENT_MONTH, START_DATE)
    date_end = datetime(CURRENT_YEAR, END_MONTH, END_DATE)

    # Format dates as needed
    date_begin_str = date_begin.strftime('%Y%m%d')
    date_end_str = date_end.strftime('%Y%m%d')

    # Build the SQL query with parameterized query
    sql_query: str = f"""
    DECLARE @DateBegin DATE = ?;
    DECLARE @DateEnd DATE = ?;

    EXEC {procedure_name}
        @DataBegin = @DateBegin,
        @DataEnd = @DateEnd;
    """

    # 💀💀💀 EXECUTION ⚠️⚠️⚠️
    result_df = pd.read_sql_query(sql_query, engine, params=(date_begin_str, date_end_str))

    # Filtering basic ones
    result_df['DataEntered'] = pd.to_datetime(result_df['DataEntered'])
    result_df = result_df[
        (result_df['DataEntered'].dt.month == CURRENT_MONTH) & (result_df['DataEntered'].dt.year == CURRENT_YEAR) &
        result_df['DocName'].isin(['Оптовая реализация', 'Финансовая скидка'])]

    # UNIQUE INNs
    # result_df.drop_duplicates(subset=['INN'], inplace=True)
    # result_df['INN'] = pd.to_numeric(result_df['INN'], errors='coerce')
    result_df = result_df[['INN']]
    time2 = time.time()
    print(f'Clients list took {round(time2 - time1, 0)} seconds.')
    return result_df
