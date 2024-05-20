import logging
import logging.config
import os
import time
from datetime import datetime

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine  # For creating a connection engine

logging.config.fileConfig('config/logging_config.ini')

##################### LOADING IMPORTANT DATA ######################
# Load environment variables from the .env file
env_file_path = 'D:/Projects/.env'
load_dotenv(env_file_path)

# Load data from different sheets in 'promotion.xlsx' into DataFrames
promotion_path = r'D:\Projects\promotion.xlsx'
region_df = pd.read_excel(promotion_path, sheet_name='Region')
types_df = pd.read_excel(promotion_path, sheet_name='TYPES')

##################### ACCESS ENV VARIABLES ######################
db_server = os.getenv("DB_SERVER")
db_database = os.getenv("DB_DATABASE_SERGELI")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_port = os.getenv("DB_PORT")
db_driver_name = os.getenv("DB_DRIVER_NAME")

##################### PROCEDURE NAME ######################
procedure_name = os.getenv("TO_FINSKIDKA")  # THIS IS HOURLY DATA GATHERING


def to_finskidka_generator(start_date, end_date, current_month: bool = True, ):
    logging.info('Start generating To Finskidka')

    start_date = datetime.strptime(start_date, '%Y%m%d')
    end_date = datetime.strptime(end_date, '%Y%m%d')
    logging.info(f'Start date: {start_date}, End date: {end_date}')

    output_file_path = f'TO FINSKIDKA - {start_date.strftime("%Y%m%d")} - {end_date.strftime("%Y%m%d")}.xlsx'
    logging.info(f'Output file path: {output_file_path}')

    # Construct the connection string
    conn_str = f"mssql+pyodbc://{db_user}:{db_password}@{db_server}:{db_port}/{db_database}?driver={db_driver_name}"

    engine = create_engine(conn_str)

    YEAR = start_date.strftime('%Y')
    START_MONTH = start_date.strftime('%m')

    END_YEAR = end_date.strftime('%Y')
    END_MONTH = end_date.strftime('%m')

    sql_query = f"""
        DECLARE @DateBegin DATE = ?;
        DECLARE @DateEnd DATE = ?;

        EXEC {procedure_name}
            @DateBegin = @DateBegin,
            @DateEnd = @DateEnd;
        """

    #####################  EXECUTION  ######################
    start_time_sql = time.time()
    try:
        # Execute the query and read the data into a pandas DataFrame
        df = pd.read_sql_query(sql_query, engine, params=(start_date, end_date))
        end_time_sql = time.time()
        logging.info(
            f'SQL query execution time: {end_time_sql - start_time_sql:.2f} seconds | '
            f'Shape of DataFrame: {df.shape}'
        )
    except Exception as e:
        logging.error(f"Error executing SQL query: {e}")
        return

    df.rename(columns={'ClientManager': 'ClientMan', "ВремяОтгр.": "DataEntered"}, inplace=True)
    df['DataEntered'] = pd.to_datetime(df['DataEntered'])
    df = df[
        (df['DataEntered'].dt.year == int(YEAR)) &
        (df['DataEntered'].dt.month >= int(START_MONTH)) &
        (df['DataEntered'].dt.month <= int(END_MONTH))

        # & df['DocName'].isin(
        #     ['Оптовая реализация',
        #      'Финансовая скидка',
        #      'Возврат товара от покупателя'])
        ]
    logging.info(f'Finished Filtering DataFrame: {df.shape}')

    df = pd.merge(df, region_df[['ClientMan', 'Region']], left_on='ClientMan', right_on='ClientMan', how='left')

    df['inn_temp'] = pd.to_numeric(df['INN'], errors='coerce')
    types_df['INN_temp'] = pd.to_numeric(types_df['INN'], errors='coerce')
    df = pd.merge(df, types_df[['INN_temp', 'TYPE', 'RegionType']], left_on='inn_temp', right_on='INN_temp', how='left')

    df.fillna({'TYPE': 'ROZ'}, inplace=True)

    # df.loc[df['TYPE'] == 'ROZ', 'RegionType'] = df['Region']
    df.drop(['INN_temp', 'inn_temp'], axis=1, inplace=True)

    df.sort_values(by='DataEntered', ascending=False, inplace=True)

    logging.info(f'Saving DataFrame to Excel: {output_file_path}')
    export_time = time.time()
    df.to_excel(output_file_path, index=False)
    export_end_time = time.time()
    logging.info(f'Export time: {export_end_time - export_time:.2f} seconds')
    logging.info(f'Successfully saved DataFrame to Excel: {output_file_path}')

    ##################### FORMAT THE TABLE  ######################
    # formatter(df, output_file_path)

    ##################### MODIFIED TIME OF THE FILE ######################

    if os.path.exists(output_file_path):
        # Get the size of the file in bytes
        file_size_bytes = os.path.getsize(output_file_path)

        # Convert bytes to kilobytes, megabytes, or gigabytes for readability
        file_size_kb = file_size_bytes / 1024.0
        file_size_mb = file_size_kb / 1024.0

        # Get the last modification time in seconds since the epoch
        modification_time_seconds = os.path.getmtime(output_file_path)

        # Convert seconds since the epoch to a datetime object
        modification_time = datetime.fromtimestamp(modification_time_seconds)

        # Get the change time (metadata change time) in seconds since the epoch
        change_time_seconds = os.path.getctime(output_file_path)

        # Convert seconds since the epoch to a datetime object

        change_time = datetime.fromtimestamp(change_time_seconds)
        logging.info(
            f"File Size: {file_size_mb:.2f} MB | Last Modified Time: {modification_time.strftime('%H:%M')} | Change Time: {change_time.strftime('%H:%M')}")

    else:
        logging.error("File not found.")
    logging.info('TO FINSKIDKA generator process completed successfully')
    return output_file_path
