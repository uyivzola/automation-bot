import os
from datetime import datetime

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine

from reports.formatter import formatter


def top_generator():
    print('Started running top generator')
    env_file_path = 'D:/Projects/.env'
    load_dotenv(env_file_path)

    # Get today's date
    today_date = datetime.now().strftime('%d %b')
    output_file_path = f'TOP ostatok - {today_date}.xlsx'
    xikmat_file_path = f'TOP ostatok - Эвер-Ромфарм  - {today_date}.xlsx'

    # Access the environment variables
    db_server = os.getenv("DB_SERVER")
    db_database = os.getenv("DB_DATABASE_SERGELI")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_port = os.getenv("DB_PORT")
    db_driver_name = os.getenv("DB_DRIVER_NAME")

    # Construct the connection string
    conn_str = f"mssql+pyodbc://{db_user}:{db_password}@{db_server}:{db_port}/{db_database}?driver={db_driver_name}"

    procedure_name = "bGoodByIncome_Dilshod"
    engine = create_engine(conn_str)

    # Build the SQL query with parameterized query
    sql_query = f"""
    EXEC {procedure_name}
    """

    # 💀💀💀 EXECUTION!!! ⚠️⚠️⚠️
    result_df = pd.read_sql_query(sql_query, engine)

    # Rename columns
    result_df.columns = ['Компания', 'Код товара', 'Товар', 'Производитель', 'Серия', 'Склад', 'Субсклад',
                         'Дата прихода', 'Дней до срока годн.', 'П.Цена', 'П.Кол-во', 'На брони', 'Своб. Остаток',
                         'Selling Price']
    # Only "Асклепий" data!!!
    result_df = result_df[result_df['Компания'] == 'Асклепий']

    # Strip unnecessary spaces in 'Товар' column
    result_df['Товар'] = result_df['Товар'].str.strip()
    result_df['Производитель'] = result_df['Производитель'].str.strip()

    # Add new columns #UNIVERSAL ONE
    result_df['остаток'] = result_df['На брони'] + result_df['Своб. Остаток']
    result_df['сумма'] = result_df['П.Цена'] * result_df['остаток']

    # Group by 'Производитель' and 'Товар' and aggregate the sums
    pivoted_df = result_df.groupby(['Производитель', 'Товар']).agg({'остаток': 'sum', 'сумма': 'sum'}).reset_index()

    # Sort the DataFrame by 'Sum of сумма' in descending order
    df = pivoted_df.sort_values(by='сумма', ascending=False)

    # special for Xikmat
    manufacturers = ["Ever neuro pharma", "Ромфарм Компании - Румыния", "Ромфарм Комп/World Medicine"]
    xikmat_df = result_df[result_df['Производитель'].isin(manufacturers)]
    xikmat_df = xikmat_df.groupby(['Производитель', 'Товар', 'Selling Price']).agg(
        {'остаток': 'sum', 'сумма': 'sum'}).reset_index()

    xikmat_df.sort_values(by='сумма', ascending=False, inplace=True)

    df.to_excel(output_file_path, index=False)
    xikmat_df.to_excel(xikmat_file_path, index=False)
    formatter(df, output_file_path)
    formatter(xikmat_df, xikmat_file_path)
