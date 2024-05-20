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
    promotion_path = r'D:\Projects\promotion.xlsx'
    output_file_path_x = f'TOP ostatok - {today_date}.xlsx'
    projects_df = pd.read_excel(promotion_path, sheet_name='Projects')
    corporative_products_path = f'TOP ostatok - NIKA  - {today_date}.xlsx'
    ots_file_path = f'TOP ostatok - OTS Project - {today_date}.xlsx'
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
    corporate_manufacturers = ['Nika-Pharm',
                               'ТНК Силма /Россия',
                               'Флумед-Фарм ООО/Молдова/',
                               'Минскинтеркапс',
                               'Selo Medical Австрия',
                               'Рохто Фармасьютикал']

    corporative_products = result_df[result_df['Производитель'].isin(corporate_manufacturers)]
    corporative_products = corporative_products.groupby(['Производитель', 'Товар', 'Selling Price']).agg(
        {'остаток': 'sum', 'сумма': 'sum'}).reset_index()

    corporative_products.sort_values(by='сумма', ascending=False, inplace=True)

    df.to_excel(output_file_path_x, index=False)
    corporative_products.to_excel(corporative_products_path, index=False)
    # ots_df.to_excel(ots_file_path, index=False)
    formatter(df, output_file_path_x)
    formatter(corporative_products, corporative_products_path)

    for project in projects_df['ProjectName'].unique():
        for project_name in projects_df['ProjectName'].unique():
            project_filtered_df = result_df[
                result_df['Товар'].isin(projects_df[projects_df['ProjectName'] == project_name]['GoodName'])]
            project_filtered_df = project_filtered_df.groupby(['Производитель', 'Товар', 'Selling Price']).agg(
                {'остаток': 'sum', 'сумма': 'sum'}).reset_index()
            output_file_path = f'TOP ostatok - {project_name} - {today_date}.xlsx'
            project_filtered_df.to_excel(output_file_path, index=False)
            formatter(project_filtered_df, output_file_path)
