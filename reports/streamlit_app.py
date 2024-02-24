import os
import streamlit as st
import pandas as pd
from matplotlib import pyplot as plt
from sqlalchemy import create_engine
from dotenv import load_dotenv
from datetime import datetime, timedelta
import seaborn as sns
import os
from datetime import datetime, timedelta  # For working with dates
import matplotlib.dates as mdates
from matplotlib.dates import DateFormatter
import calendar
import plotly.express as px


##################### LOADING IMPORTANT DATA ######################
# Load environment variables from the .env file
env_file_path = 'D:/Projects/.env'
load_dotenv(env_file_path)
# Giving output file name
output_file_path = 'ZAKAZ.xlsx'
# Load data from different sheets in 'promotion.xlsx' into DataFrames
promotion_path = r'D:\Projects\promotion.xlsx'
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

##################### DATE - JANUARY ######################
CURRENT_MONTH = datetime.now().month
CURRENT_YEAR = datetime.now().year
_, days_in_month = calendar.monthrange(CURRENT_YEAR, CURRENT_MONTH)

date_begin = datetime(CURRENT_YEAR, CURRENT_MONTH, 1)
date_end = datetime(CURRENT_YEAR, CURRENT_MONTH, days_in_month)
##################### CONNECTION STRING AND SQL QUERY ######################
# Construct the connection string

conn_str = f"mssql+pyodbc://{db_user}:{db_password}@{db_server}:{db_port}/{db_database}?driver={db_driver_name}"
engine = create_engine(conn_str)

sql_query: str = f"""
DECLARE @DateBegin DATETIME = ?;
DECLARE @DateEnd DATETIME = ?;
EXEC bGoodSaleWithInfo 
@DataBegin = @DateBegin, @DataEnd = @DateEnd;
"""


@st.cache_data
def run_query(start_date, end_date):
    # Execute the SQL query with provided dates
    x=st.text('RUNNING')
    print('Running...')
    df = pd.read_sql_query(sql_query.format(procedure_name=procedure_name), engine,
                           params=(start_date, end_date))
    del x
    # Extract year, month, and day components from start_date and end_date
    start_year, start_month, start_day = start_date.year, start_date.month, start_date.day
    end_year, end_month, end_day = end_date.year, end_date.month, end_date.day

    # Define conditions for filtering
    date_conditions = (
            (df['DataEntered'].dt.year == start_year) &
            (df['DataEntered'].dt.month.between(start_month, end_month)) &
            (df['DataEntered'].dt.day.between(start_day, end_day))
    )

    doc_conditions = df['DocName'].isin(['Оптовая реализация', 'Финансовая скидка'])
    manager_condition = ~df['InvoiceManager'].isin(['Бочкарева Альвина'])
    admin_condition = ~df['ClientManager'].isin(['Администратор'])
    price_condition = (df['OutPrice'] >= 20_000)

    df = pd.merge(df, region_df[['ClientMan', 'Region']], left_on='ClientManager', right_on='ClientMan',
                  how='left')

    df['inn_temp'] = pd.to_numeric(df['INN'], errors='coerce')
    types_df['INN_temp'] = pd.to_numeric(types_df['INN'], errors='coerce')
    df = pd.merge(df, types_df[['INN_temp', 'TYPE', 'RegionType']], left_on='inn_temp',
                  right_on='INN_temp',
                  how='left')

    df.fillna({'TYPE': 'ROZ'}, inplace=True)

    df.loc[df['TYPE'] == 'ROZ', 'RegionType'] = df['Region']

    df['OXVAT'] = df['INN'].map(df['INN'].value_counts())

    categorical_columns = ['Office', 'DocName', 'GoodId', 'Good', 'Producer', 'INN', 'Client', 'City', 'ClientType',
                           'InvoiceManager', 'ClientManager', 'Store', 'StoreDep', 'DownPayment', 'PaymentTerm',
                           'Region',
                           'RegionType', 'TYPE']

    df[categorical_columns] = df[categorical_columns].astype('category')

    columns_to_drop = ([col for col in df.columns if col.endswith('_temp')] +
                       ['ClientMan', 'Region', 'YY', 'MM', 'Data',
                        'SerialNo', 'City', 'ClientType', 'Store', 'StoreDep',
                        'InClient', 'Number',
                        'Postavshik'
                        ])
    df = df[date_conditions & doc_conditions & manager_condition & admin_condition & price_condition]

    # # Drop the identified columns
    df.drop(columns=columns_to_drop, inplace=True)
    return df


def format_large_numbers(value, *pos):
    if value >= 1e9:  # If the value is in billions
        return f'{value / 1e9:.1f}B'
    elif value >= 1e6:  # If the value is in millions
        return f'{value / 1e6:.1f}M'
    elif value >= 1e3:  # If the value is in thousands
        return f'{value / 1e3:.1f}K'
    else:  # For values less than 1000
        return str(int(value))


def abbreviate_good_name(name, max_words=3):
    words = name.split()
    if len(words) <= max_words:
        return name
    else:
        return ' '.join(words[:max_words]) + '...'


# Set default start_date to the first day of the current month
default_start_date = datetime.now().replace(day=1)

# Date range selection
start_date = st.date_input("Select start date", default_start_date)
end_date = st.date_input("Select end date")

# Convert date objects to datetime objects
start_date = datetime.combine(start_date, datetime.min.time())
end_date = datetime.combine(end_date, datetime.max.time())


@st.cache_data
def calc_to_by_regions(df: pd.DataFrame, type_value: str):
    st.text(type_value)
    result_df = df[df['TYPE'] == type_value]
    return result_df


@st.cache_data
def calc_daily_totals(df):
    goods_totals = df.groupby('Good', observed=False)['OutKolich'].sum().reset_index()
    goods_totals = goods_totals[goods_totals['OutKolich'] >= 2500]
    top_goods = goods_totals.sort_values(by='OutKolich', ascending=False)

    daily_total_df = df[df['Good'].isin(top_goods['Good'])].groupby(
        ['Good', df['DataEntered'].dt.date],
        observed=False)[
        'OutKolich'].sum().reset_index()
    daily_total_df = daily_total_df.sort_values(by='OutKolich', ascending=False)
    daily_total_df = daily_total_df[daily_total_df['OutKolich'] >= 20]

    return daily_total_df



if st.button("Run Query"):
    # Run the SQL query and display the DataFrame
    df = run_query(start_date, end_date)
    st.text('Whole DATAFRAME')
    st.dataframe(df)

    for type_value in ['ROZ']:
        frame = calc_to_by_regions(df, type_value)
        daily_totals = calc_daily_totals(frame)

        st.dataframe(daily_totals)
        for good in daily_totals['Good'].unique():
            st.text(good)
            # fig = px.bar(daily_totals[daily_totals['Good'] == good], x='DataEntered', y='OutKolich',
            #              title=f"Sales of {good} from {start_date.strftime('%d.%b')} to {end_date.strftime('%d.%b')}",
            #              color_discrete_sequence=px.colors.qualitative.G10)
            #
            # Create a bar plot using Seaborn
            fig, ax = plt.subplots(figsize=(12, 8))
            sns.barplot(data=daily_totals[daily_totals['Good'] == good], x='DataEntered', y='OutKolich')

            # Customize other plot properties
            ax.set_title(f"Sales of {good} from {start_date.strftime('%d.%b')} to {end_date.strftime('%d.%b')}")
            ax.set_xlabel('Date')
            ax.set_ylabel('Total Quantity (OutKolich)')

            # Show the plot using st.pyplot()
            st.pyplot(fig)
