import os
import sys
import pandas as pd
import numpy as np
from pathlib import Path
from IPython.display import display


pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', 100)
pd.set_option('display.float_format', '{:.9f}'.format)

# Function to list all directories within the parent directory
def list_dirs(parent_directory, pattern="2024*"):
    all_directories = [str(path) for path in Path(parent_directory).rglob(pattern)]
    return all_directories

# Function to read the csv files matching the pattern
def select_row(file_path):
    df = pd.read_csv(file_path)

    # Remove rows with log_time less than "2024-01-01 00:00:00"
    df["log_time"] = pd.to_datetime(df["log_time"], format="%Y-%m-%d %H:%M:%S")
    df["time_only"] = df["log_time"].dt.strftime("%H:%M:%S.%f")

    start_time = "09:17:00.000000"
    end_time = "15:28:00.000000"

    df = df[(df["time_only"] >= start_time) & (df["time_only"] <= end_time)]

    # Apply the conditions as per the R script
    df = df[(df["ap"] > df["bp"]) & (df["bp"] > 0)]
    df = df[(df["ask.1000"] > df["bid.1000"]) & (df["bid.1000"] > 0)]
    df = df[(df["ask.5000"] > df["bid.5000"]) & (df["bid.5000"] > 0)]
    df = df[(df["ask.10000"] > df["bid.10000"]) & (df["bid.10000"] > 0)]
    df = df[(df["ask.30000"] > df["bid.30000"]) & (df["bid.30000"] > 0)]

    return df

# Bucketcor function implementation
def bucketcor(df, col, original_col, returns_cols, num_buckets=5):
    split = 1 / num_buckets
    breaks = df[col].quantile(np.arange(0, 1 + split, split)).unique()

    if len(breaks) < 3:
        print(f"Insufficient unique breaks to create meaningful buckets for column: {col}")
        return None

    labels = breaks[1:]
    df['group'] = pd.cut(df[col], bins=breaks, labels=labels, include_lowest=True)
    df = df[~df['group'].isna()]
    
    # Initialize DataFrame with 'group' column
    correlations = pd.DataFrame({'group': df['group'].unique()})
    correlations = correlations.sort_values('group').reset_index(drop=True)
    
    # For each return_col, calculate the correlation and add as a new column
    for return_col in returns_cols:
        corr_series = df.groupby('group')[[original_col, return_col]].corr().iloc[0::2, -1].reset_index(drop=True)
        correlations[return_col] = corr_series.values

    # Convert 'group' to float for proper formatting
    correlations['group'] = correlations['group'].astype(float)
    
    return correlations

def main(parent_directory):
    all_directories = list_dirs(parent_directory)

    csv_files = [os.path.join(dir_path, file) for dir_path in all_directories for file in os.listdir(dir_path) if file.startswith("balance_") and file.endswith(".log")]

    # Pick only the first 10 files (if applicable)
    # csv_files = csv_files[:10]

    print("Reading the CSV files")

    # Load or read data
    if os.path.exists("df.parquet"):
        df = pd.read_parquet("df.parquet", allow_truncated_timestamps=True)
    else:
        df = pd.concat([select_row(file) for file in csv_files], ignore_index=True)
        df.to_parquet("df.parquet", allow_truncated_timestamps=True)
        print("Data saved as df.parquet")

    # Drop unwanted columns
    columns_to_drop = [
        'ap', 'bp', 'aq', 'bq', 'ref',
        'bid.1000', 'bidsz.1000', 'ask.1000', 'asksz.1000', 'ref.1000',
        'bid.5000', 'bidsz.5000', 'ask.5000', 'asksz.5000', 'ref.5000',
        'bid.10000', 'bidsz.10000', 'ask.10000', 'asksz.10000', 'ref.10000',
        'bid.30000', 'bidsz.30000', 'ask.30000', 'asksz.30000', 'ref.30000'
    ]
    df = df.drop(columns=columns_to_drop, errors='ignore')

    # Alphas to check
    alphas_to_check = [
        "balance_sd_5_over_300", "balance_sd_5_over_600", "balance_sd_5_over_1800",
        "vol_std_weighted_return", "normPrice_marketVol_ratio", "balance_with_thresholds"
    ]

    # Create absolute columns for all alphas
    for alpha in alphas_to_check:
        df[f"abs_{alpha}"] = df[alpha].abs()

    print("Calculating bucketcor for all alphas")

    # Calculate bucketcor for all alphas with return columns
    return_cols = ['return.1000', 'return.5000', 'return.10000', 'return.30000']
    for alpha in alphas_to_check:
        alpha_abs_col = f"abs_{alpha}"
        df_filtered = df[[alpha_abs_col, alpha] + return_cols]
        result = bucketcor(df_filtered, alpha_abs_col, alpha, return_cols)
        if result is not None:
            print(f"Bucketcor result for alpha {alpha}:")
            display(result)
        else:
            print(f"No valid result for alpha: {alpha}")

    # Calculate bucketcor for z-score conditions
    for alpha in alphas_to_check:
        alpha_abs_col = f"abs_{alpha}"
        df_filtered = df[[alpha_abs_col, alpha] + return_cols]

        # Calculate z-score
        df_filtered[f"z_score_{alpha}"] = (df_filtered[alpha_abs_col] - df_filtered[alpha_abs_col].mean()) / df_filtered[alpha_abs_col].std()

        # Bucketcor for z-score <= 3
        print(f"Calculating bucketcor for z-score <= 3 for alpha: {alpha}")
        r1 = bucketcor(df_filtered[df_filtered[f"z_score_{alpha}"] <= 3], alpha_abs_col, alpha, return_cols)
        if r1 is not None:
            print(f"Bucketcor result for z-score <= 3 for alpha {alpha}:")
            display(r1)
        else:
            print(f"No valid result for alpha: {alpha}")

        # Bucketcor for z-score > 3
        print(f"Calculating bucketcor for z-score > 3 for alpha: {alpha}")
        r2 = bucketcor(df_filtered[df_filtered[f"z_score_{alpha}"] > 3], alpha_abs_col, alpha, return_cols)
        if r2 is not None:
            print(f"Bucketcor result for z-score > 3 for alpha {alpha}:")
            display(r2)
        else:
            print(f"No valid result for alpha: {alpha}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please provide the path to the CSV file as an argument.")
        sys.exit(1)
    parent_directory = sys.argv[1]
    main(parent_directory)
