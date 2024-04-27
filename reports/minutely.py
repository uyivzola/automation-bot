import time
import pandas as pd


def load_data_from_excel() -> pd.DataFrame:
    df = pd.read_excel('./minutely.xlsx')
    return df


last_processed_data = None


def check_for_updates():
    global last_processed_data

    current_data = load_data_from_excel()

    if last_processed_data is None:
        last_processed_data = current_data
        return False

    new_invoices = current_data[~current_data.isin(last_processed_data)].dropna()
    if not new_invoices.empty:
        print('New invoices detected:')
        for _, row in new_invoices.iterrows():
            print(f"Invoice Number '{row['Invoice Number']}' added at {row['TIME']} with Total Amount: {row['TotalAmount']}")
        last_processed_data = pd.concat([last_processed_data, new_invoices], ignore_index=True)
        return True
    else:
        return False


def main():
    while True:
        check_for_updates()


if __name__ == "__main__":
    main()
