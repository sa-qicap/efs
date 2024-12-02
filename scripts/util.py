import pandas as pd

import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os
import re
import pandas as pd
import numpy as np
import warnings
from scipy.stats import zscore
from sklearn.linear_model import LinearRegression


class PythonUtil:

    def merge_mddv(df):
        contract_master = pd.read_csv('/global/data/reference_data/contract_data/NSEFNO/old_platform/2024_09_06_NSE_FNO_CONTRACT_MASTER.csv')
        cm_contract_master = pd.read_csv('/global/data/reference_data/contract_data/NSECM/old_platform/2024_09_06_NSE_CM_CONTRACT_MASTER.csv')

        df['contract'] = df['contract'].apply(lambda x: re.sub(r'NSE_', '', x))

        for c in df['contract'].unique():

            # merge mddv
            matching_rows = contract_master[(contract_master['symbol'] == c) & (contract_master['type'] == 'FUT')]
            if not matching_rows.empty:
                df.loc[df['contract'] == c, 'moving_daily_volume'] = matching_rows['moving_daily_volume'].values[0]
            else:
                # Handle the case where no match is found
                print(f"No matching symbol found for contract: {c}")
                df.loc[df['contract'] == c, 'moving_daily_volume'] = None  # Or assign a default value
            
            # merge sector
            matching_rows = cm_contract_master[(cm_contract_master['symbol'] == c) ]
            if not matching_rows.empty:
                df.loc[df['contract'] == c, 'sector'] = matching_rows['sector'].values[0]
            else:
                print(f"No matching symbol found for contract: {c}")
                df.loc[df['contract'] == c, 'sector'] = None  # Or assign a default value

        return df

    def bucketcor(df, col, x, y, numBuckets=5):
        # Calculate the quantile breaks
        breaks = df[col].quantile(np.linspace(0, 1, numBuckets + 1)).unique()
        
        # Check if there are enough unique breaks
        if len(breaks) < 3:
            warnings.warn(f"Insufficient unique breaks to create meaningful buckets for column: {col}")
            return None
        
        # Define labels for the buckets
        labels = breaks[1:].astype(str)
        
        # Create a copy of the DataFrame to avoid modifying the original
        df1 = df
        
        # Create the 'group' column by binning 'col' based on the breaks
        df1['group'] = pd.cut(df1[col], bins=breaks, labels=labels, include_lowest=True)
        
        # Remove rows where 'group' is NaN
        df1 = df1[df1['group'].notna()]

        # number of points in first group
        print("Number of points in first group:")
        print(len(df1[df1['group'] == labels[0]]))

        
        # Group by 'group' and calculate the correlation between 'x' and each column in 'y' within each group
        def compute_correlations(group):
            correlations = {}
            for y_col in y:
                corr = group[x].corr(group[y_col])
                correlations[y_col] = corr
            return pd.Series(correlations)
        
        df2 = df1.groupby('group').apply(compute_correlations).reset_index()

        # add a row with mean of all columns
        df2.loc['mean'] = df2.mean()
        
        return df2
    
    def bucketcor2(df, col1, col2, x, y, numBuckets=5):
        # Calculate the quantile breaks
        breaks1 = df[col1].quantile(np.linspace(0, 1, numBuckets + 1)).unique()
        
        # Check if there are enough unique breaks
        if len(breaks1) < 3:
            warnings.warn(f"Insufficient unique breaks to create meaningful buckets for column: {col1}")
            return None
        
        # Define labels for the buckets
        labels1 = breaks1[1:].astype(str)
        
        # Create a copy of the DataFrame to avoid modifying the original
        df1 = df
        
        # Create the 'group' column by binning 'col' based on the breaks
        df1['group1'] = pd.cut(df1[col1], bins=breaks1, labels=labels1, include_lowest=True)
        
        # Remove rows where 'group' is NaN
        df1 = df1[df1['group1'].notna()]
        
        
        for g in labels1:
            pts = df1[df1['group1'] == g]
            print(f"Current group for {col1}: {g}")
            print(PythonUtil.bucketcor(pts, col2, x, y, numBuckets))


    def get_df_with_groups(df, alpha, numBuckets=5):

        abs_col = "abs." + alpha
        df[abs_col] = df[alpha].abs()
        col = abs_col

        # Calculate the quantile breaks
        breaks = df[col].quantile(np.linspace(0, 1, numBuckets + 1)).unique()
        
        # Check if there are enough unique breaks
        if len(breaks) < 3:
            warnings.warn(f"Insufficient unique breaks to create meaningful buckets for column: {col}")
            return None
        
        # Define labels for the buckets
        labels = breaks[1:].astype(str)
        
        # Create a copy of the DataFrame to avoid modifying the original
        df1 = df.copy()
        
        # Create the 'group' column by binning 'col' based on the breaks
        df1['group'] = pd.cut(df1[col], bins=breaks, labels=labels, include_lowest=True)
        
        # Remove rows where 'group' is NaN
        df1 = df1[df1['group'].notna()]
        
        return df1


    def calculate_buckets(df_in, alpha):
        import warnings
        
        # Calculate absolute values and z-scores for the 'alpha' column
        abs_col = "abs." + alpha
        df_in[abs_col] = df_in[alpha].abs()

        df_in['z_score_alpha'] = (df_in[alpha] - df_in[alpha].mean()) / df_in[alpha].std(ddof=1)
        
        # Define the list of return columns
        returns = [
            'return.1000', 'return.5000', 'return.10000', 'return.30000',
            'return.60000', 'return.300000', 'return.600000', 'return.900000',
            'return.1800000'
        ]
        
        # Select only the required columns
        df = df_in[[alpha, abs_col] + returns + ['z_score_alpha']]
        
        print("Total number of points:")
        print(len(df))
        
        # Calculate bucket correlations
        print(f"Calculating bucketcor for alpha: {alpha}")
        r = PythonUtil.bucketcor(df, abs_col, alpha, returns, numBuckets=5)
        if r is not None:
            print(r)
        else:
            print(f"No valid result for alpha: {alpha}")
        
        # Filter the dataframe into two parts based on z-score values
        df_le_3 = df[df['z_score_alpha'].abs() <= 3]
        df_gt_3 = df[df['z_score_alpha'].abs() > 3]
        pts_gt3 = len(df_gt_3)
        dates_gt3 = len(df_in[df_in['z_score_alpha'].abs() > 3]['date_only'].unique())
        
        print(f"Total number of points with z-score <= 3: {len(df_le_3)}")
        print(f"Total number of points with z-score > 3: {pts_gt3}")
        print(f"Number of unique dates in dfgt3: {dates_gt3}")
        
        # Calculate bucket correlations for z-score <= 3
        print(f"Calculating bucketcor for z-score <= 3 for alpha: {alpha}")
        r1 = PythonUtil.bucketcor(df_le_3, abs_col, alpha, returns)
        if r1 is not None:
            print(r1)
        else:
            print(f"No valid result for alpha: {alpha}")
        
        # Calculate bucket correlations for z-score > 3
        print(f"Calculating bucketcor for z-score > 3 for alpha: {alpha}")
        r2 = PythonUtil.bucketcor(df_gt_3, abs_col, alpha, returns)
        if r2 is not None:
            print(r2)
        else:
            print(f"No valid result for alpha: {alpha}")


    def get_gt3_alpha(df, alpha):
        df['z_score_alpha'] = (df[alpha] - df[alpha].mean()) / df[alpha].std(ddof=1)
        df_gt_3 = df[df['z_score_alpha'].abs() > 3]
        return df_gt_3
            

    def remove_cols(df, patterns):
        for pattern in patterns:
            # Use filter with regex to find columns matching the pattern
            matching_cols = df.filter(regex=pattern).columns
            df = df.drop(columns=matching_cols)
        return df
    

    def keep_cols(df, patterns):
        for pattern in patterns:
            # Use filter with regex to find columns matching the pattern
            matching_cols = df.filter(regex=pattern).columns
            df2 = df[matching_cols]
        return df2


    def load_and_concat_to_feather(dir_list, pattern):
        # Construct a pattern to match files that start with the given pattern
        full_pattern = r'^' + re.escape(pattern) + r'.*\.log$'
        # print(full_pattern)
        
        csv_files = []
        for dir_path in dir_list:
            # List all files in the directory
            try:
                files_in_dir = os.listdir(dir_path)
            except FileNotFoundError:
                print(f"Directory not found: {dir_path}")
                continue
            # Filter files matching the pattern
            matching_files = [f for f in files_in_dir if re.match(full_pattern, f)]
            # Get full paths
            full_paths = [os.path.join(dir_path, f) for f in matching_files]
            csv_files.extend(full_paths)
        print("CSV Files:", csv_files)
        
        feather_files = []
        for csv_file in csv_files:
            feather_file = csv_file[:-4] + '.feather'  # Assumes .log is 4 characters

            if os.path.exists(feather_file):
                print(f"Feather file already exists: {feather_file}")
                feather_files.append(feather_file)
                continue

            # Process each CSV file
            df = PythonUtil.select_row(csv_file)
            # Generate a Feather file name (replace .log with .feather)
            
            df.reset_index(drop=True, inplace=True)

            # Save DataFrame to Feather format
            df.to_feather(feather_file)
            feather_files.append(feather_file)
        
        print("Feather Files:", feather_files)
        
        # Load the Feather files and concatenate
        df_list = [pd.read_feather(f) for f in feather_files]
        df_combined = pd.concat(df_list, ignore_index=True, sort=False)
        
        return df_combined

    def select_row_unchecked(file_path):
        # Load the data
        df = pd.read_csv(file_path)

        # Convert 'log_time' to datetime
        df['log_time'] = pd.to_datetime(df['log_time'], format="%Y-%m-%d %H:%M:%S")

        # Filter rows with 'log_time' greater than or equal to '2024-01-01 00:00:00'
        df = df[df['log_time'] >= '2024-01-01 00:00:00']

        # Create 'time_only' column in the format 'HH:MM:SS'
        df['time_only'] = df['log_time'].dt.strftime('%H:%M:%S.%f')
        df['date_only'] = df['log_time'].dt.strftime('%Y-%m-%d')

        # Define start and end times
        start_time = "10:00:00.000000000"
        end_time = "15:58:00.000000000"

        # Filter rows based on 'time_only' between start_time and end_time
        df = df[(df['time_only'] >= start_time) & (df['time_only'] <= end_time)]

        # # Apply conditions for 'ap', 'bp', 'ask.1000', 'bid.1000', etc.
        # df = df[(df['ask'] > df['bid']) & (df['bid'] > 0)]
        # df = df[(df['ask.1000'] > df['bid.1000']) & (df['bid.1000'] > 0)]
        # df = df[(df['ask.5000'] > df['bid.5000']) & (df['bid.5000'] > 0)]
        # df = df[(df['ask.10000'] > df['bid.10000']) & (df['bid.10000'] > 0)]
        # df = df[(df['ask.30000'] > df['bid.30000']) & (df['bid.30000'] > 0)]

        df = PythonUtil.remove_cols(df, ['ask', 'bid', 'ref', 'log_level'])

        df = df.drop_duplicates()
        df = df.reset_index(drop=True)

        return df

    def select_row(file_path):
        # Load the data
        df = pd.read_csv(file_path)

        # Convert 'log_time' to datetime
        df['log_time'] = pd.to_datetime(df['log_time'], format="%Y-%m-%d %H:%M:%S")

        # Filter rows with 'log_time' greater than or equal to '2024-01-01 00:00:00'
        df = df[df['log_time'] >= '2024-01-01 00:00:00']

        # Create 'time_only' column in the format 'HH:MM:SS'
        df['time_only'] = df['log_time'].dt.strftime('%H:%M:%S.%f')
        df['date_only'] = df['log_time'].dt.strftime('%Y-%m-%d')

        # Define start and end times
        start_time = "10:00:00.000000000"
        end_time = "15:58:00.000000000"

        # check df has rows before start time
        if len(df[df['time_only'] < start_time]) == 0 or len(df[df['time_only'] > end_time]) == 0:
            print("DF is missing rows before start time or after end time: ", file_path)


        # Filter rows based on 'time_only' between start_time and end_time
        df = df[(df['time_only'] >= start_time) & (df['time_only'] <= end_time)]

        # Apply conditions for 'ap', 'bp', 'ask.1000', 'bid.1000', etc.
        df = df[(df['ask'] > df['bid']) & (df['bid'] > 0)]
        df = df[(df['ask.1000'] > df['bid.1000']) & (df['bid.1000'] > 0)]
        df = df[(df['ask.5000'] > df['bid.5000']) & (df['bid.5000'] > 0)]
        df = df[(df['ask.10000'] > df['bid.10000']) & (df['bid.10000'] > 0)]
        df = df[(df['ask.30000'] > df['bid.30000']) & (df['bid.30000'] > 0)]

        df = PythonUtil.remove_cols(df, ['ask', 'bid', 'ref', 'log_level'])

        df = df.drop_duplicates()
        df = df.reset_index(drop=True)

        return df
    

    def convert_log_time(log_time_str):
        # Check if log_time is already a datetime object
        if isinstance(log_time_str, datetime):
            return log_time_str  # Return as-is if already in the correct format
        else:
            log_time_str = log_time_str[:26]  # Truncate to remove extra digits
            return datetime.strptime(log_time_str, '%Y-%m-%d %H:%M:%S.%f')

    def plot_compare_mids(a, mid1, mid2, selected_contract=None, selected_time=None):
        # Apply the conversion to the log_time column
        a['log_time'] = a['log_time'].apply(PythonUtil.convert_log_time)

        # pick the first name in contracts
        if selected_contract is None:
            selected_contract = a['contract'].iloc[0]
        
        # Create a figure and axis
        fig, ax1 = plt.subplots(figsize=(14, 7))

        # filter the data for the selected contract
        print("contract:"  + selected_contract)
        a = a[a['contract'] == selected_contract]

        # Plot `fc` on the first y-axis
        ax1.plot(a['log_time'], a[mid1], color='blue', label=mid1)
        ax1.plot(a['log_time'], a[mid2], color='red', label=mid2)
        ax1.set_xlabel('Log Time')
        ax1.set_ylabel('r', color='blue')
        ax1.tick_params(axis='y', labelcolor='blue')

        ax1.legend()

        if selected_time is not None:
            t = PythonUtil.convert_log_time(selected_time)
            ax1.axvline(x=t, color='green', linestyle='--')

        # Create a second y-axis for `fi`
        # ax2 = ax1.twinx()
        # ax2.plot(a['log_time'], a['r_ema'], color='red', label='fi')
        # ax2.set_ylabel('r_ema', color='red')
        # ax2.tick_params(axis='y', labelcolor='red')

        fig.tight_layout()
        plt.show()


    def plot_compare_3_mids(a, mid1, mid2, mid3, selected_contract=None, selected_time=None):
        # Apply the conversion to the log_time column
        a['log_time'] = a['log_time'].apply(PythonUtil.convert_log_time)

        # pick the first name in contracts
        if selected_contract is None:
            selected_contract = a['contract'].iloc[0]
        
        # Create a figure and axis
        fig, ax1 = plt.subplots(figsize=(14, 7))

        # filter the data for the selected contract
        print("contract:"  + selected_contract)
        a = a[a['contract'] == selected_contract]

        # Plot `fc` on the first y-axis
        ax1.plot(a['log_time'], a[mid1], color='blue', label=mid1)
        ax1.plot(a['log_time'], a[mid2], color='red', label=mid2)
        ax1.plot(a['log_time'], a[mid3], color='orange', label=mid3)
        ax1.set_xlabel('Log Time')
        ax1.set_ylabel('r', color='blue')
        ax1.tick_params(axis='y', labelcolor='blue')

        ax1.legend()

        if selected_time is not None:
            t = PythonUtil.convert_log_time(selected_time)
            ax1.axvline(x=t, color='green', linestyle='--')

        # Create a second y-axis for `fi`
        # ax2 = ax1.twinx()
        # ax2.plot(a['log_time'], a['r_ema'], color='red', label='fi')
        # ax2.set_ylabel('r_ema', color='red')
        # ax2.tick_params(axis='y', labelcolor='red')

        fig.tight_layout()
        plt.show()



    def plot_only_mid(a, mid, selected_contract=None, selected_time=None):
        fig, ax1 = plt.subplots(figsize=(14, 7))

        if selected_contract is None:
            selected_contract = a['contract'].iloc[0]
        
        # filter the data for the selected contract
        print("contract:"  + selected_contract)
        a = a[a['contract'] == selected_contract]

        # Plot `fc` on the first y-axis
        ax1.plot(a['log_time'], a[mid], color='blue', label=mid)
        ax1.set_xlabel('Log Time')
        ax1.set_ylabel(mid, color='blue')
        ax1.tick_params(axis='y', labelcolor='blue')

        if selected_time is not None:
            t = PythonUtil.convert_log_time(selected_time)
            ax1.axvline(x=t, color='green', linestyle='--')


        ax1.legend()

        # Create a second y-axis for `fi`
        # ax2 = ax1.twinx()
        # ax2.plot(a['log_time'], a['r_ema'], color='red', label='fi')
        # ax2.set_ylabel('r_ema', color='red')
        # ax2.tick_params(axis='y', labelcolor='red')

        fig.tight_layout()
        plt.show()


    def plot_only_alpha(a, alpha_name, selected_contract=None):
        # Function to convert log_time string to a datetime object, ignoring extra fractional digits

        # Apply the conversion to the log_time column
        a['log_time'] = a['log_time'].apply(PythonUtil.convert_log_time)

        # pick the first name in contracts
        if selected_contract is None:
            selected_contract = a['contract'].iloc[0]

        # filter the data for the selected contract
        print(selected_contract)
        a = a[a['contract'] == selected_contract]

        # Create a figure and axis
        fig, ax1 = plt.subplots(figsize=(14, 7))

        # Plot the alpha values as a bar chart on the left y-axis
        colors = ['green' if alpha >= 0 else 'red' for alpha in a[alpha_name]]
        # colors2 = []
        # for r in a.iterrows():
        #     if r[1]['time_only'] == '15:26:54':
        #         colors2 += ['purple']
        #     elif r[1]['ratio_diff'] > 0:
        #         colors2 += ['green']
        #     else:
        #         colors2 += ['red']
            
        ax1.bar(a['log_time'], a[alpha_name], color=colors, width=0.00001, label='Alpha')

        # Label for the left y-axis (Alpha)
        ax1.set_ylabel('Alpha')

        # Formatting the x-axis for better time visibility
        ax1.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%H:%M:%S'))

        plt.xticks(rotation=45)

        # Add a title and make the layout tighter
        plt.title('Alpha and Mid Price Over Time')
        fig.tight_layout()

        # Show the plot
        plt.show()

    
    def plot_alpha_with_mid(a, alpha_name, mid, selected_contract=None):
        # Function to convert log_time string to a datetime object, ignoring extra fractional digits
        a['log_time'] = a['log_time'].apply(PythonUtil.convert_log_time)

        if selected_contract is None:
            selected_contract = a['contract'].iloc[0]

        # filter the data for the selected contract
        print(selected_contract)
        a = a[a['contract'] == selected_contract]

        # Create a figure and axis
        fig, ax1 = plt.subplots(figsize=(14, 7))

        # Plot the alpha values as a bar chart on the left y-axis
        colors = ['green' if alpha >= 0 else 'red' for alpha in a[alpha_name]]
        # colors2 = []
        # for r in a.iterrows():
        #     if r[1]['time_only'] == '15:26:54':
        #         colors2 += ['purple']
        #     elif r[1]['ratio_diff'] > 0:
        #         colors2 += ['green']
        #     else:
        #         colors2 += ['red']
            
        ax1.bar(a['log_time'], a[alpha_name], color=colors, width=0.00001, label='Alpha')

        # Label for the left y-axis (Alpha)
        ax1.set_ylabel('Alpha')

        # Create a second y-axis for the mid prices
        ax2 = ax1.twinx()

        # Plot the mid prices as a line chart on the right y-axis
        ax2.plot(a['log_time'], a[mid], color='blue', label='Mid Price', linewidth=1.5)

        # Label for the right y-axis (Mid Prices)
        ax2.set_ylabel('Mid Price')

        ax1.legend(loc='upper left')
        ax2.legend(loc='upper right')

        # Formatting the x-axis for better time visibility
        ax1.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%H:%M:%S'))

        plt.xticks(rotation=45)

        # Add a title and make the layout tighter
        plt.title('Alpha and Mid Price Over Time')
        fig.tight_layout()

        # Show the plot
        plt.show()


#####################
# linear regression
#####################

def find_best_feature(signals_to_select_from, signals_selected, df, label):
    best_feature = None
    best_correlation = -np.inf
    y = df[label]
    for feature in signals_to_select_from:
        X = df[signals_selected + [feature]]
        model = LinearRegression().fit(X, y)
        combined_signal = np.dot(X, model.coef_)
        correlation = np.corrcoef(combined_signal, y)[0, 1]
        if correlation > best_correlation:
            best_correlation = correlation
            best_feature = feature
    return best_feature, best_correlation

def select_top_features(df, features, label_col, top_n=5):
    signals_selected = []
    signals_to_select_from = features.copy()
    while len(signals_selected) < top_n and signals_to_select_from:
        print(len(signals_selected), end=' ')
        best_feature, _ = find_best_feature(signals_to_select_from, signals_selected, df, label_col)
        print("signals selected:", signals_selected)
        if best_feature:
            signals_selected.append(best_feature)
            signals_to_select_from.remove(best_feature)