import os
import time
from datetime import datetime, timedelta  # For working with dates

import pandas as pd  # For working with DataFrames
from dotenv import load_dotenv
from openpyxl import Workbook
from openpyxl.styles import NamedStyle, PatternFill, Border, Side, Alignment
from openpyxl.utils import get_column_letter
from sqlalchemy import create_engine

from reports.google_sheets import write_df_to_google_sheet, upload_to_google_sheet


def top_product_sold_generator():
    ##################### LOADING IMPORTANT DATA ######################
    # Load environment variables from the .env file
    env_file_path = 'D:/Projects/.env'
    load_dotenv(env_file_path)
    # Giving output file name
    # Load data from different sheets in 'promotion.xlsx' into DataFrames
    promotion_path = 'D:\Projects\promotion.xlsx'
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
    procedure_name = 'zAdmReportDFS_short'  # THIS IS HOURLY DATA GATHERING
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
    df.columns = ['DocumentType', 'Invoice Number', 'Goodid', 'Good', 'Manufacturer', 'inn', 'ClientName',
                  'SalesManager', 'ClientMan', 'PaymentTerm', 'BasePrice', 'SellingPrice', 'Quantity', 'DateEntered',
                  'BaseAmount', 'TotalAmount']

    ##################### BASIC FILTER ######################
    df = df[df['DocumentType'].isin(['Оптовая реализация', 'Финансовая скидка'])]
    df['DateEntered'] = pd.to_datetime(df['DateEntered'])
    # Filter the DataFrame for today's date
    today_date = datetime.today().strftime("%Y-%m-%d")
    df = df[(df['DateEntered'].dt.date == pd.to_datetime(today_date).date()) & df['SalesManager'] != '']

    df = pd.merge(df, region_df[['ClientMan', 'Region']], left_on='ClientMan', right_on='ClientMan', how='left')

    df['inn_temp'] = pd.to_numeric(df['inn'], errors='coerce')
    types_df['INN_temp'] = pd.to_numeric(types_df['INN'], errors='coerce')
    df = pd.merge(df, types_df[['INN_temp', 'TYPE', 'RegionType']], left_on='inn_temp', right_on='INN_temp', how='left')
    df['TYPE'].fillna('ROZ', inplace=True)
    df.loc[df['TYPE'] == 'ROZ', 'RegionType'] = df['Region']

    df['OXVAT'] = df['inn'].map(df['inn'].value_counts())

    categorical_columns = ['DocumentType', 'Good', 'Manufacturer', 'inn', 'ClientName', 'SalesManager', 'ClientMan',
                           'PaymentTerm', 'Region', 'RegionType', 'TYPE']

    df[categorical_columns] = df[categorical_columns].astype('category')
    # Assuming df is your DataFrame
    columns_to_drop = [col for col in df.columns if col.endswith('_temp')]

    # Drop the identified columns
    df.drop(columns=columns_to_drop, inplace=True)

    top_revenue_products(df=df)
    high_volume_products(df=df)
    client_fav_products(df=df)


def top_revenue_products(df, output_file_path='TOP_REVENUE_PRODUCTS_SOLD.xlsx'):
    print("Creating TOP REVENUE PRODUCTS LIST🔝")
    # Record the start time
    start_time = time.time()

    # Create a new workbook and remove the default sheet
    workbook = Workbook()
    default_sheet = workbook.active
    workbook.remove(default_sheet)

    # Iterate over unique types in the dataframe
    for i, type_value in enumerate(sorted(df['TYPE'].unique()), start=1):

        # Filter dataframe for the current type
        type_df = df[df['TYPE'] == type_value]
        print(f"Processing sheet: {type_value}, DataFrame shape: {type_df.shape}")

        # Assuming df is the DataFrame obtained from the SQL query
        # result_df = type_df[['Good', 'TotalAmount', 'ClientMan', 'RegionType']]
        result_df = type_df.copy()
        print(f"Result DataFrame shape: {result_df.shape}")

        # Group by Good and Region, then sum the TotalAmount
        grouped_df = result_df.groupby(['Good', 'RegionType', 'ClientMan'], observed=False).agg(
            {'TotalAmount': 'sum'}).reset_index()
        print(f"Grouped DataFrame shape: {grouped_df.shape}")

        # Create a pivot table
        pivot_table = pd.pivot_table(grouped_df, values='TotalAmount', index=['Good'], columns=['RegionType'],
                                     aggfunc='sum', fill_value=0)
        print(f"Pivot Table shape: {pivot_table.shape}")

        # Drop the 'Admin' column
        pivot_table.drop(columns=['Админ'], inplace=True, errors='ignore')

        # Calculate Grand Total
        pivot_table['TOTAL'] = pivot_table.sum(axis=1)
        # Sort by 'TOTAL' in descending order
        pivot_table.sort_values(by='TOTAL', ascending=False, inplace=True)

        # Reorder the columns
        pivot_table = pivot_table[['TOTAL'] + list(pivot_table.columns[:-1])]

        # Exclude columns with total 0 in the pivot_table
        pivot_table = pivot_table.loc[:, (pivot_table != 0).any(axis=0)]
        pivot_table = pivot_table.loc[(pivot_table != 0).any(axis=1)]
        pivot_table.reset_index(drop=False, inplace=True)
        pivot_table.index += 1
        pivot_table.index.name = '#'
        print(f"Sheet {i} name: {type_value}")

        # Create a new sheet with the type name
        worksheet = workbook.create_sheet(title=str(type_value))
        colors_for_sheet = ['FFC4C4', 'F3B95F', 'EAFFD0']

        worksheet.sheet_properties.tabColor = colors_for_sheet[i - 1]
        # Create a new named style for the header
        header_style = NamedStyle(name=f'header_style_{i}',
                                  fill=PatternFill(start_color=colors_for_sheet[i - 1],
                                                   end_color=colors_for_sheet[i - 1], fill_type='solid'))

        # Add pivot table to the sheet
        for row_idx, (index, values) in enumerate(pivot_table.iterrows(), start=2):
            worksheet.cell(row=row_idx, column=1, value=index)

            # Iterate through the values and add them to the respective columns
            for col_idx, (col, value) in enumerate(values.items(), start=2):
                worksheet.cell(row=row_idx, column=col_idx, value=value)

        # Add headers for the pivot table
        for col_idx, col_name in enumerate(pivot_table.columns, start=2):
            worksheet.cell(row=1, column=col_idx, value=col_name)

        # Apply the header style to the first row
        for cell in worksheet[1]:
            cell.style = header_style
            cell.alignment = Alignment(horizontal='center', vertical='center')

        # 2. Autofit all columns
        for column in worksheet.columns:
            max_length = 0
            column = [cell for cell in column]
            for cell in column:
                try:
                    value = str(cell.value)
                    if len(value) > max_length:
                        max_length = len(value)
                except:
                    pass
            adjusted_width = (max_length + 1.5)
            column_letter = get_column_letter(column[0].column)
            worksheet.column_dimensions[column_letter].width = adjusted_width

        # 3. Format columns with thousands separators
        number_format = NamedStyle(name=f'number_format_{i}', number_format='### ### ### ##0')

        # Specify the columns to format based on float64 datatype
        float64_columns = pivot_table.select_dtypes(include=['float64']).columns

        for col in float64_columns:
            col_index = pivot_table.columns.get_loc(col) + 2  # 1-based index, starting from column 2
            col_letter = get_column_letter(col_index)

            for cell in worksheet[col_letter][1:]:  # Start from the second row assuming the first row is headers
                try:
                    formatted_value = "{:,.2f}".format(float(cell.value))
                    cell.value = float(cell.value)
                    cell.style = number_format
                except (ValueError, TypeError) as error:
                    print(error)

        # Apply background color to all cells in the TOTAL (2nd) column
        for row in worksheet.iter_rows(min_row=1, max_row=16, min_col=1,
                                       max_col=3):
            for cell in row:
                cell.fill = PatternFill(start_color=colors_for_sheet[i - 1], end_color=colors_for_sheet[i - 1],
                                        fill_type='solid')

        # Add borders to all cells with data
        for row in worksheet.iter_rows(min_row=1, max_row=worksheet.max_row, min_col=1,
                                       max_col=worksheet.max_column):
            for cell in row:
                cell.border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'),
                                     bottom=Side(style='thin'))

    try:
        # Save the workbook
        workbook.save(output_file_path)
        end_time = time.time()

        # Calculate and print the elapsed time
        elapsed_time = round(end_time - start_time, 2)
        print(f"Process took: {elapsed_time} seconds.\n Love you <3. Have a nice day, babe 💋❤️")
    except Exception as e:
        print(f"Error saving workbook: {e}")


def client_fav_products(df, output_file_path='CLIENT_FAVORITE_PRODUCTS.xlsx'):
    print("Creating Pivot Tables and Exporting🎨....")
    # Record the start time
    start_time = time.time()

    # Create a new workbook and remove the default sheet
    workbook = Workbook()
    default_sheet = workbook.active
    workbook.remove(default_sheet)

    # Iterate over unique types in the dataframe
    for i, type_value in enumerate(sorted(df['TYPE'].unique()), start=1):

        # Filter dataframe for the current type
        type_df = df[df['TYPE'] == type_value]
        print(f"Processing sheet: {type_value}, DataFrame shape: {type_df.shape}")

        # Assuming df is the DataFrame obtained from the SQL query
        result_df = type_df.copy()
        print(f"Result DataFrame shape: {result_df.shape}")

        # Group by Good and Region, then count the unique 'inn'
        grouped_df = result_df.groupby(['Good', 'RegionType'], observed=False).agg({'inn': 'nunique'}).reset_index()
        print(f"Grouped DataFrame shape: {grouped_df.shape}")

        # Create a pivot table
        pivot_table = pd.pivot_table(grouped_df, index='Good', columns='RegionType', values='inn', aggfunc='sum',
                                     fill_value=0)
        print(f"Pivot Table shape: {pivot_table.shape}")

        # Drop the 'Admin' column
        pivot_table.drop(columns=['Админ'], inplace=True, errors='ignore')

        # Calculate Grand Total
        pivot_table['TOTAL CLIENTS'] = pivot_table.sum(axis=1)

        # Sort by 'TOTAL' in descending order
        pivot_table.sort_values(by='TOTAL CLIENTS', ascending=False, inplace=True)

        # Reorder the columns
        pivot_table = pivot_table[['TOTAL CLIENTS'] + list(pivot_table.columns[:-1])]

        # Exclude columns with total 0 in the pivot_table
        pivot_table = pivot_table.loc[:, (pivot_table != 0).any(axis=0)]
        pivot_table = pivot_table.loc[(pivot_table != 0).any(axis=1)]
        pivot_table.reset_index(drop=False, inplace=True)
        pivot_table.index += 1
        pivot_table.index.name = '#'
        print(f"Sheet {i} name: {type_value}")

        # Create a new sheet with the type name
        worksheet = workbook.create_sheet(title=str(type_value))
        colors_for_sheet = ['FFC4C4', 'F3B95F', 'EAFFD0']

        worksheet.sheet_properties.tabColor = colors_for_sheet[i - 1]
        # Create a new named style for the header
        header_style = NamedStyle(name=f'header_style_{i}',
                                  fill=PatternFill(start_color=colors_for_sheet[i - 1],
                                                   end_color=colors_for_sheet[i - 1], fill_type='solid'))

        # Add pivot table to the sheet
        for row_idx, (index, values) in enumerate(pivot_table.iterrows(), start=2):
            worksheet.cell(row=row_idx, column=1, value=index)

            # Iterate through the values and add them to the respective columns
            for col_idx, (col, value) in enumerate(values.items(), start=2):
                worksheet.cell(row=row_idx, column=col_idx, value=value)
        #
        # Add pivot table to the sheet
        # for row_idx, values in enumerate(pivot_table.values, start=2):
        #     # Iterate through the values and add them to the respective columns
        #     for col_idx, value in enumerate(values, start=1):  # Start from 1 to skip the index column
        #         worksheet.cell(row=row_idx, column=col_idx, value=value)

        # Add headers for the pivot table
        for col_idx, col_name in enumerate(pivot_table.columns, start=2):  # Start from 1 to skip the index column
            worksheet.cell(row=1, column=col_idx, value=col_name)

        # Apply the header style to the first row
        for cell in worksheet[1]:
            cell.style = header_style
            cell.alignment = Alignment(horizontal='center', vertical='center')

        # 2. Autofit all columns
        for column in worksheet.columns:
            max_length = 0
            column = [cell for cell in column]
            for cell in column:
                try:
                    value = str(cell.value)
                    if len(value) > max_length:
                        max_length = len(value)
                except:
                    pass
            adjusted_width = (max_length + 1.8)
            column_letter = get_column_letter(column[0].column)
            worksheet.column_dimensions[column_letter].width = adjusted_width

        # 3. Format columns with thousands separators
        number_format = NamedStyle(name=f'number_format_{i}', number_format='### ### ### ##0')

        # Specify the columns to format based on float64 datatype
        float64_columns = pivot_table.select_dtypes(include=['float64']).columns

        for col in float64_columns:
            col_index = pivot_table.columns.get_loc(col) + 2  # 1-based index, starting from column 2
            col_letter = get_column_letter(col_index)

            for cell in worksheet[col_letter][1:]:  # Start from the second row assuming the first row is headers
                try:
                    formatted_value = "{:,.2f}".format(float(cell.value))
                    cell.value = float(cell.value)
                    cell.style = number_format
                except (ValueError, TypeError) as error:
                    print(error)

        # Apply background color to all cells in the TOTAL (2nd) column
        for row in worksheet.iter_rows(min_row=1, max_row=26, min_col=1,
                                       max_col=3):
            for cell in row:
                cell.fill = PatternFill(start_color=colors_for_sheet[i - 1], end_color=colors_for_sheet[i - 1],
                                        fill_type='solid')

        # Add borders to all cells with data
        for row in worksheet.iter_rows(min_row=1, max_row=worksheet.max_row, min_col=1, max_col=worksheet.max_column):
            for cell in row:
                cell.border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'),
                                     bottom=Side(style='thin'))

    try:
        # Save the workbook
        workbook.save(output_file_path)
        end_time = time.time()

        # Calculate and print the elapsed time
        elapsed_time = round(end_time - start_time, 2)
        print(f"Process took: {elapsed_time} seconds.\n Love you <3. Have a nice day, babe 💋❤️")
    except Exception as e:
        print(f"Error saving workbook: {e}")


def high_volume_products(df, output_file_path='HIGH_VOLUME_PRODUCTS.xlsx'):
    print("Creating High Volume and Exporting🎨....")
    # Record the start time
    start_time = time.time()

    # Create a new workbook and remove the default sheet
    workbook = Workbook()
    default_sheet = workbook.active
    workbook.remove(default_sheet)

    # Iterate over unique types in the dataframe
    for i, type_value in enumerate(sorted(df['TYPE'].unique()), start=1):

        # Filter dataframe for the current type
        type_df = df[df['TYPE'] == type_value]
        print(f"Processing sheet: {type_value}, DataFrame shape: {type_df.shape}")

        # Assuming df is the DataFrame obtained from the SQL query
        result_df = type_df.copy()
        print(f"Result DataFrame shape: {result_df.shape}")

        # Group by Good and Region, then count the unique 'inn'
        grouped_df = result_df.groupby(['Good', 'RegionType'], observed=False).agg({'Quantity': 'sum'}).reset_index()
        print(f"Grouped DataFrame shape: {grouped_df.shape}")

        # Create a pivot table
        pivot_table = pd.pivot_table(grouped_df, index='Good', columns='RegionType', values='Quantity', aggfunc='sum',
                                     fill_value=0)
        print(f"Pivot Table shape: {pivot_table.shape}")

        # Drop the 'Admin' column
        pivot_table.drop(columns=['Админ'], inplace=True, errors='ignore')

        # Calculate Grand Total
        pivot_table['TOTAL QUANTITY'] = pivot_table.sum(axis=1)

        # Sort by 'TOTAL' in descending order
        pivot_table.sort_values(by='TOTAL QUANTITY', ascending=False, inplace=True)

        # Reorder the columns
        pivot_table = pivot_table[['TOTAL QUANTITY'] + list(pivot_table.columns[:-1])]

        # Exclude columns with total 0 in the pivot_table
        pivot_table = pivot_table.loc[:, (pivot_table != 0).any(axis=0)]
        pivot_table = pivot_table.loc[(pivot_table != 0).any(axis=1)]
        pivot_table.reset_index(drop=False, inplace=True)
        pivot_table.index += 1
        pivot_table.index.name = '#'
        print(f"Sheet {i} name: {type_value}")

        # Create a new sheet with the type name
        worksheet = workbook.create_sheet(title=str(type_value))
        colors_for_sheet = ['FFC4C4', 'F3B95F', 'EAFFD0']

        worksheet.sheet_properties.tabColor = colors_for_sheet[i - 1]
        # Create a new named style for the header
        header_style = NamedStyle(name=f'header_style_{i}',
                                  fill=PatternFill(start_color=colors_for_sheet[i - 1],
                                                   end_color=colors_for_sheet[i - 1], fill_type='solid'))

        # Add pivot table to the sheet
        for row_idx, (index, values) in enumerate(pivot_table.iterrows(), start=2):
            worksheet.cell(row=row_idx, column=1, value=index)

            # Iterate through the values and add them to the respective columns
            for col_idx, (col, value) in enumerate(values.items(), start=2):
                worksheet.cell(row=row_idx, column=col_idx, value=value)
        #
        # Add pivot table to the sheet
        # for row_idx, values in enumerate(pivot_table.values, start=2):
        #     # Iterate through the values and add them to the respective columns
        #     for col_idx, value in enumerate(values, start=1):  # Start from 1 to skip the index column
        #         worksheet.cell(row=row_idx, column=col_idx, value=value)

        # Add headers for the pivot table
        for col_idx, col_name in enumerate(pivot_table.columns, start=2):  # Start from 1 to skip the index column
            worksheet.cell(row=1, column=col_idx, value=col_name)

        # Apply the header style to the first row
        for cell in worksheet[1]:
            cell.style = header_style
            cell.alignment = Alignment(horizontal='center', vertical='center')

        # 2. Autofit all columns
        for column in worksheet.columns:
            max_length = 0
            column = [cell for cell in column]
            for cell in column:
                try:
                    value = str(cell.value)
                    if len(value) > max_length:
                        max_length = len(value)
                except:
                    pass
            adjusted_width = (max_length + 1.8)
            column_letter = get_column_letter(column[0].column)
            worksheet.column_dimensions[column_letter].width = adjusted_width

        # 3. Format columns with thousands separators
        number_format = NamedStyle(name=f'number_format_{i}', number_format='### ### ### ##0')

        # Specify the columns to format based on float64 datatype
        float64_columns = pivot_table.select_dtypes(include=['float64']).columns

        for col in float64_columns:
            col_index = pivot_table.columns.get_loc(col) + 2  # 1-based index, starting from column 2
            col_letter = get_column_letter(col_index)

            for cell in worksheet[col_letter][1:]:  # Start from the second row assuming the first row is headers
                try:
                    formatted_value = "{:,.2f}".format(float(cell.value))
                    cell.value = float(cell.value)
                    cell.style = number_format
                except (ValueError, TypeError) as error:
                    print(error)

        # Apply background color to all cells in the TOTAL (2nd) column
        for row in worksheet.iter_rows(min_row=1, max_row=26, min_col=1,
                                       max_col=3):
            for cell in row:
                cell.fill = PatternFill(start_color=colors_for_sheet[i - 1], end_color=colors_for_sheet[i - 1],
                                        fill_type='solid')

        # Add borders to all cells with data
        for row in worksheet.iter_rows(min_row=1, max_row=worksheet.max_row, min_col=1, max_col=worksheet.max_column):
            for cell in row:
                cell.border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'),
                                     bottom=Side(style='thin'))

    try:
        # Save the workbook
        workbook.save(output_file_path)
        end_time = time.time()

        # Calculate and print the elapsed time
        elapsed_time = round(end_time - start_time, 2)
        print(f"Process took: {elapsed_time} seconds.\n")
    except Exception as e:
        print(f"Error saving workbook: {e}")
