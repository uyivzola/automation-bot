import logging
import logging.config
import os
import time
from datetime import datetime

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine

# Load logging configuration from file
logging.config.fileConfig('config/logging_config.ini')

env_file_path = 'D:/Projects/.env'
load_dotenv(env_file_path)

# Load data from different sheets in 'promotion.xlsx' into DataFrames
promotion_path = r'D:\Projects\promotion.xlsx'
region_df = pd.read_excel(promotion_path, sheet_name='Region')
aksiya_df = pd.read_excel(promotion_path, sheet_name='Aksiya')
paket_df = pd.read_excel(promotion_path, sheet_name='Paket')
types_df = pd.read_excel(promotion_path, sheet_name='TYPES')

##### CONNECTION STRING AND SQL QUERY ######################
db_server = os.getenv("DB_SERVER")
db_database = os.getenv("DB_DATABASE_ASKGLOBAL")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_port = os.getenv("DB_PORT")
db_driver_name = os.getenv("DB_DRIVER_NAME")

####### PROCEDURE NAME ######################
procedure_name = os.getenv("MONTHLY")


def monthly_generator(start_date, end_date, current_month: bool = True, ):
    logging.info('Started running monthly generator')

    start_date = datetime.strptime(start_date, '%Y%m%d')
    end_date = datetime.strptime(end_date, '%Y%m%d')
    logging.info(f'Start date: {start_date}, End date: {end_date}')

    output_file_path = f'SALES - Monthly - {start_date.strftime("%Y%m%d")} - {end_date.strftime("%Y%m%d")}.xlsx'
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
        @DataBegin = @DateBegin,
        @DataEnd = @DateEnd;
    """

    ########  EXECUTION  ######################
    start_time_sql = time.time()
    df = pd.read_sql_query(sql_query, engine, params=(start_date, end_date))
    end_time_sql = time.time()
    logging.info(
        f'SQL query execution time: {end_time_sql - start_time_sql:.2f} seconds | '
        f'Shape of DataFrame: {df.shape}')

    ######## BASIC FILTER ######################
    df['DataEntered'] = pd.to_datetime(df['DataEntered'])
    df = df[
        (df['DataEntered'].dt.year == int(YEAR)) &
        (df['DataEntered'].dt.month >= int(START_MONTH)) &
        (df['DataEntered'].dt.month <= int(END_MONTH)) &
        df['DocName'].isin(
            ['Оптовая реализация',
             'Финансовая скидка',
             'Возврат товара от покупателя'])]
    logging.info(f'Finished Filtering DataFrame: {df.shape}')

    logging.info('Merging DataFrames...')
    df.rename(columns={'GoodId': 'Goodid', 'ClientManager': 'ClientMan', 'INN': 'inn'}, inplace=True)
    region_df['ClientMan'] = region_df['ClientMan'].str.title()

    df['ClientMan'] = df['ClientMan'].str.title()
    df = pd.merge(df, region_df[['ClientMan', 'Region']], left_on='ClientMan', right_on='ClientMan', how='left')

    df = pd.merge(df, aksiya_df[['Goodid', 'Aksiya']], left_on='Goodid', right_on='Goodid', how='left')

    df = pd.merge(df, paket_df[['Goodid', 'Paket']], left_on='Goodid', right_on='Goodid', how='left')

    logging.info('Performing advanced filtering and formatting...')
    df['OXVAT'] = df['inn'].map(df['inn'].value_counts())
    df['inn_temp'] = pd.to_numeric(df['inn'], errors='coerce')
    types_df['INN_temp'] = pd.to_numeric(types_df['INN'], errors='coerce')
    df = pd.merge(df, types_df[['INN_temp', 'TYPE', 'RegionType']], left_on='inn_temp', right_on='INN_temp', how='left')
    df['TYPE'] = df['TYPE'].fillna('ROZ', inplace=True)
    df.loc[df['TYPE'] == 'ROZ', 'RegionType'] = df['Region']

    df.drop(['INN_temp', 'inn_temp', 'Postavshik', 'Store', 'City', 'SerialNo', 'ClientType', 'InPrice', 'FSkidka',
             'InClient', 'BaseMarkUp'], axis=1, inplace=True)
    logging.info('Finished advanced filtering and formatting')
    logging.info(f'DF columns: {df.columns}')
    # Save DataFrame to Excel
    logging.info(f'Saving DataFrame to Excel: {output_file_path}')
    df.to_excel(output_file_path, index=False)
    logging.info(f'Successfully saved DataFrame to Excel: {output_file_path}')

    # Call formatter function
    # logging.info('Calling formatter function...')
    # formatter(df, output_file_path)
    # logging.info(f'Successfully formatted: {output_file_path}')

    # Return output file path
    logging.info(f'{monthly_generator.__name__} process completed successfully')
    return output_file_path
