source('/efs/sameer.arora/scripts/util.R')
library('plyr')
library('dplyr')
library(data.table)
# Function to create absolute column
getBucketCor <- function(df, column_name) {

    print("creating absolute column")
    # Check if column exists in dataframe
    if (column_name %in% colnames(df)) {
        # Create absolute column
        df[, paste("abs.", column_name, sep = "") := abs(get(column_name))]
    } else {
        stop("Column not found in dataframe.")
    }

    print(paste("Calculating bucketcor for alpha:", column_name))
    result <- bucketcor(df, paste("abs.", column_name, sep = ""), column_name, c('return.1000', 'return.5000', 'return.10000', 'return.30000'))
    if (!is.null(result)) {
        print(result)
    } else {
        print(paste("No valid result for alpha:", alpha))
    }
}

