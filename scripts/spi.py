import pandas as pd
pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)
import os.path
import datetime
import argparse
import SPI_my_machine


from datetime import datetime, timedelta

def string_to_date(date_str):
    try:
        return datetime.strptime(date_str, "%Y%m%d")
    except ValueError:
        raise ValueError("Date must be in YYYYMMDD format")


def main():
    parser = argparse.ArgumentParser(description="Process date in YYYYMMDD format.")
    parser.add_argument("date_str", type=str, help="Date in YYYYMMDD format")
    args = parser.parse_args()

    start_date = string_to_date(args.date_str)
    end_date = string_to_date(args.date_str)

    day_delta = timedelta(days=1)
    current_date = start_date

    bod_file = pd.DataFrame()

    underlying = "NIFTY"

    if underlying == "BANKNIFTY":
        underlying_folder_name = "NIFTY_BANK"
    elif underlying == "FINNIFTY":
        underlying_folder_name = "NIFTY_FINANCIAL_SERVICES"
    elif underlying == "NIFTY":
        underlying_folder_name = "NIFTY_50"
    elif underlying == "MIDCPNIFTY":
        underlying_folder_name = "NIFTY_MIDCAP_SELECT"

    while current_date <= end_date:
        datestring = current_date.strftime('%Y%m%d')
        iisl_location = SPI_my_machine.iisl_location(datestring, underlying_folder_name)
        if not os.path.isfile(iisl_location):
            print(f"{iisl_location}  IISL File is Missing for {underlying}")
        else:
            # new_bod_file = SPI_my_machine.parse_index_cm_contracts_from_date(datestring, "NIFTY")
            new_bod_file = SPI_my_machine.parse_index_cm_contracts_from_date(datestring, underlying)

            new_bod_file["current_date"] = datestring
            new_bod_file.to_csv(f"/efs/sameer.arora/IndexData/{underlying}{datestring}.csv", index=False)

            bod_file = pd.concat([bod_file, new_bod_file], ignore_index=True)

            print(datestring)
        
        current_date += day_delta

if __name__ == "__main__":
    main()
