import calendar
import os
from datetime import datetime  # For working with dates

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine

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
plan_df = pd.read_excel(promotion_path, sheet_name='Plan')

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

st.set_page_config(
    page_title="Ex-stream-ly Cool App",
    page_icon="⭐",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.extremelycoolapp.com/help',
        'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "# This is a header. This is an *extremely* cool app!"
    }
)

sql_query: str = """
    SELECT O.Name                    as Base,
           D.Name                    AS DocKind,
           i.Number                  AS InvoiceNumber,
           G.GoodId                  as Goodid,
           G.Name                    AS GoodName,
           M.Name                    AS Producer,
           C.Inn                     as Inn,
           C.FindName                AS ClientName,
           PIM.Name                  AS InvoiceManager,
           PCM.Name                  AS ClientManager,
           I.PaymentTerm,
           il.pBasePrice             as BasePrice,
           il.Price                  as SellingPrice,
           il.Kolich                 AS Quantity,
           I.DataEntered            AS DataEntered,
           il.pBasePrice * il.Kolich AS BaseAmount,
           il.pSumma                 AS TotalAmount
    FROM INVOICELN il
             JOIN INVOICE i ON il.InvoiceId = i.InvoiceId
             JOIN PERSONAL PIM ON i.PersonalId = PIM.PersonalId
             JOIN DOCKIND D ON i.DocKindId = D.DocKindId
             JOIN CLIENT C ON i.ClientId = C.ClientId
             JOIN INCOMELN incl ON il.IncomeLnId = incl.IncomeLnId
             JOIN Good G ON incl.GoodId = G.GoodId
             JOIN Producer M ON M.ProducerId = G.ProducerId
             JOIN PERSONAL PCM ON C.PersonalId = PCM.PersonalId
             join OFFICE O on C.OfficeId = O.OfficeId
    
        WHERE YEAR(I.DataEntered) = 2024
              and MONTH(I.DataEntered) = 3
              and D.name IN ('Финансовая скидка', 'Оптовая реализация', 'Возврат товара от покупателя')
            order by i.DataEntered desc;
"""


@st.cache_data
def run_query(start_date=datetime(2024, 2, 1).strftime('%Y%m%d'),
              end_date=datetime(2024, 3, 31).strftime('%Y%m%d')) -> pd.DataFrame:
    # Execute the SQL query with provided dates
    x = st.text('RUNNING')
    print('Running...')
    df = pd.read_sql_query(sql_query.format(procedure_name=procedure_name), engine,
                           # params=(start_date, end_date)
                           )
    df['DataEntered'] = pd.to_datetime(df['DataEntered'])
    df = pd.merge(df, region_df[['ClientMan', 'Region']], left_on='ClientManager', right_on='ClientMan',
                  how='left')
    df = df[~(df['Region'] == 'Админ')]
    return df


def format_large_numbers(value, *pos) -> str:
    if value >= 1e9:  # If the value is in billions
        return f'{value / 1e9:.1f}B'
    elif value >= 1e6:  # If the value is in millions
        return f'{value / 1e6:.1f}M'
    elif value >= 1e3:  # If the value is in thousands
        return f'{value / 1e3:.1f}K'
    else:  # For values less than 1000
        return str(int(value))


def abbreviate_good_name(name, max_words=3) -> str:
    words = name.split()
    if len(words) <= max_words:
        return name
    else:
        return ' '.join(words[:max_words]) + '...'


df = run_query()
#
# total_sales = df.groupby(['Region'], observed=False)['TotalAmount'].sum()
#
# yesterday_sales = \
#     df[df['DataEntered'].dt.date == (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')].groupby('Region',
#                                                                                                        observed=False)[
#         'TotalAmount'].sum()
#
# # Merging the two DataFrames on the 'Region' column
# merged_df = pd.merge(total_sales, plan_df, on='Region', how='left')
#
# options = st.multiselect('Which regions do you want to see?',
#                          merged_df['Region'].unique(),
#                          )
# selected_data = merged_df[merged_df['Region'].isin(options)]
#
# # Streamlit dashboard
# st.title('Sales Analysis Dashboard')
#
# # Display Gauge Chart for each region
# for index, row in selected_data.iterrows():
#     if row["Region"] != 'Админxs':
#         fig = go.Figure(go.Indicator(
#             mode="gauge+number",
#             value=row['TotalAmount'],
#             domain={'x': [0, 1], 'y': [0, 1]},
#             title={'text': f'{row["Region"]} Sales'},
#             gauge={
#                 'axis': {
#                     'range': [0, row['PlanSales']],
#                     'tickfont': {
#                         'size': 22
#                     }},
#                 'bar': {'color': "green"},
#                 'steps': [
#                     {'range': [0, row['PlanSales'] * 0.8], 'color': "lightgray"},
#                     {'range': [row['PlanSales'] * 0.8, row['PlanSales'] * 0.9], 'color': "gray"}],
#                 'threshold': {
#                     'line': {'color': "green", 'width': 2},
#                     'thickness': 0.75,
#                     'value': row['PlanSales']}
#             }
#         ))
#
#         st.plotly_chart(fig)

# Assuming 'DataEntered' is in datetime format, otherwise convert it.
df['DataEntered'] = pd.to_datetime(df['DataEntered'])

# Create figure
fig = go.Figure()

# Iterate over unique regions and add a trace for each one
for region in df['Region'].unique():
    region_data = df[df['Region'] == region]
    fig.add_trace(
        go.Scatter(x=region_data['DataEntered'], y=region_data['TotalAmount'], mode='lines', name=region)
    )

# Set title
fig.update_layout(
    title_text="Daily Sales for Each Region"
)

# Add range slider
fig.update_layout(
    xaxis=dict(
        rangeselector=dict(
            buttons=list([
                dict(count=1,
                     label="1 kun",
                     step="day",
                     stepmode="backward"),
                dict(count=5,
                     label="5d",
                     step="day",
                     stepmode="backward"),
                dict(count=1,
                     label="1y",
                     step="year",
                     stepmode="backward"),
                dict(step="all")
            ])
        ),
        rangeslider=dict(
            visible=True
        ),
        type="date"
    )
)
st.plotly_chart(fig)
total_sales = df.groupby(['Region'], observed=False)['TotalAmount'].sum().reset_index()
labels = total_sales['Region'].tolist()
values = total_sales['TotalAmount'].tolist()

# pull is given as a fraction of the pie radius
figx = go.Figure(data=[go.Pie(labels=labels, values=values, pull=[1, 1, 0, 0])])
figx.update_layout(title_text="Total Sales by Region")
st.plotly_chart(figx)
# st.title()

st.balloons()
st.snow()
st.toast('Mr Stay-Puft')
st.error('Error message')
st.warning('Warning message')
st.info('Info message')
st.success(body=f"TOTAL SALES: {format_large_numbers(sum(values))}")

@st.cache_data
def calc_to_by_regions(df: pd.DataFrame, type_value: str) -> pd.DataFrame:
    st.text(type_value)
    result_df = df[df['TYPE'] == type_value]
    return result_df


@st.cache_data
def calc_daily_totals(df) -> pd.DataFrame:
    goods_totals = df.groupby('Good', observed=False)['OutKolich'].sum().reset_index()
    goods_totals = goods_totals[goods_totals['OutKolich'] >= 2500]
    top_goods = goods_totals.sort_values(by='OutKolich', ascending=False)

    daily_total_df = df[df['Good'].isin(top_goods['Good'])].groupby(
        ['Good', df['DataEntered'].dt.date],
        observed=False)[
        'OutKolich'].sum().reset_index()
    # daily_total_df = daily_total_df.sort_values(by='OutKolich', ascending=False)
    daily_total_df = daily_total_df[daily_total_df['OutKolich'] >= 20]

    return daily_total_df
