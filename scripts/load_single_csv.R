
source('/efs/sameer.arora/scripts/util.R')
library('data.table')
library('plyr')
library('dplyr')
# Check if the script has been provided with the correct number of arguments
args <- commandArgs(trailingOnly = TRUE)

if (length(args) == 0) {
  stop("Please provide the path to the CSV file as an argument.")
}

# Use the first argument as the CSV file path
parent_directory = "."
csv_files <- args[1]

# Check if the file exists
if (!file.exists(csv_files)) {
  stop("The provided file does not exist. Please check the path.")
}

# csv_files <- unlist(lapply(matched_directories, function(dir) {
#   list.files(path = dir, pattern = "^back_ret_5.*\\.log$", full.names = TRUE)
# }))

# pick only first 10 files
# csv_files <- csv_files[1:10]

select_row <- function(file) {
  df <- fread(file, skip = 0, select = NULL, nrows = Inf)

  # remove rows with log time less than 2024-01-01 00:00:00
  df$log_time <- as.POSIXct(df$log_time, format = "%Y-%m-%d %H%M%OS")
  df$time_only <- format(df$log_time, format = "%H:%M:%OS")

  start_time <- "09:17:00.000000000"
  end_time <- "15:28:00.000000000"

  df <- df[df$time_only >= start_time & df$time_only <= end_time]

  # # ap > bp & bp > 0
  df <- df[df$ap > df$bp & df$bp > 0]
  df <- df[df$ask.1000 > df$bid.1000 & df$bid.1000 > 0]
  df <- df[df$ask.5000 > df$bid.5000 & df$bid.5000 > 0]
  df <- df[df$ask.10000 > df$bid.10000 & df$bid.10000 > 0]
  df <- df[df$ask.30000 > df$bid.30000 & df$bid.30000 > 0]

  return(df)
}

print("Reading the CSV files")

# Use fread to read the CSV file
df <- rbindlist(lapply(csv_files, select_row), use.names = TRUE, fill = TRUE)
head(df)

# drop columns
df <- df %>% select(-ap, -bp, -aq, -bq, -ref, -bid.1000, -bidsz.1000, -ask.1000, -asksz.1000, ref.1000, -bid.5000, -bidsz.5000, -ask.5000, -asksz.5000, -ref.5000, -bid.10000, -bidsz.10000, -ask.10000, -asksz.10000, -ref.10000, -bid.30000, -bidsz.30000, -ask.30000, -asksz.30000, -ref.30000)

# save the combined data to a R data file
print("save the df")
save(df, file = "df.RData")

  
# take the alphas to check for as a string argument (separated by commas)
alphas_to_check <- c("balance.EQ") 


# create absolute columns for all alphas
for (alpha in alphas_to_check) {
  df[, paste("abs.", alpha, sep = "") := abs(get(alpha))]
}


print("Calculating bucketcor for all alphas")


# calculate bucketcor for all absolute alphas, with return.1000, return.5000, return.10000, return.30000
for (alpha in alphas_to_check) {
  print(paste("Calculating bucketcor for alpha:", alpha))
  result <- bucketcor(df, paste("abs.", alpha, sep = ""), alpha, c('return.1000', 'return.5000', 'return.10000', 'return.30000'))
  
  if (!is.null(result)) {
    print(result)
  } else {
    print(paste("No valid result for alpha:", alpha))
  }
}


# for each alpha, calculate the z-score and bucketcor for z-score <= 3 and z-score > 3
# for each alpha, calculate the z-score and bucketcor for z-score <= 3 and z-score > 3
for (alpha in alphas_to_check) {
  
  # Calculate z-score for all absolute alphas
  df[, paste("z_score_", alpha, sep = "") := (get(paste("abs.", alpha, sep = "")) - mean(get(paste("abs.", alpha, sep = "")), na.rm = TRUE)) / sd(get(paste("abs.", alpha, sep = "")), na.rm = TRUE)]

  # Calculate bucketcor for z-score <= 3
  print(paste("Calculating bucketcor for z-score <= 3 for alpha: ", alpha))
  r1 <- bucketcor(df[get(paste("z_score_", alpha, sep = "")) <= 3], paste("abs.", alpha, sep = ""), alpha, c('return.1000','return.5000','return.10000','return.30000'))
  if (!is.null(r1)) {
    print(r1)
  } else {
    print(paste("No valid result for alpha:", alpha))
  }

  # Calculate bucketcor for z-score > 3
  print(paste("Calculating bucketcor for z-score > 3 for alpha: ", alpha))
  r2 <- bucketcor(df[get(paste("z_score_", alpha, sep = "")) > 3], paste("abs.", alpha, sep = ""), alpha, c('return.1000','return.5000','return.10000','return.30000'))
  if (!is.null(r2)) {
    print(r2)
  } else {
    print(paste("No valid result for alpha:", alpha))
  }
}



# calculate bucketcorr for regular, IOC and Abp orders
# paste("bucketcor(df[df$type == 0], \"abs.vol_mean_5\", \"vol_mean_5\", c('return.1000','return.5000','return.10000','return.30000'))")
# bucketcor(df[df$type == 0], "abs.vol_mean_5", "vol_mean_5", c('return.1000','return.5000','return.10000','return.30000'))

# paste("bucketcor(df[df$type == 1], \"abs.vol_mean_5\", \"vol_mean_5\", c('return.1000','return.5000','return.10000','return.30000'))")
# bucketcor(df[df$type == 1], "abs.vol_mean_5", "vol_mean_5", c('return.1000','return.5000','return.10000','return.30000'))

# paste("bucketcor(df[df$type == 2], \"abs.vol_mean_5\", \"vol_mean_5\", c('return.1000','return.5000','return.10000','return.30000'))")
# bucketcor(df[df$type == 2], "abs.vol_mean_5", "vol_mean_5", c('return.1000','return.5000','return.10000','return.30000'))

# # with balance_5
# paste("bucketcor(df[df$type == 0], \"abs.balance_5\", \"balance_5\", c('return.1000','return.5000','return.10000','return.30000'))")
# bucketcor(df[df$type == 0], "abs.balance_5", "balance_5", c('return.1000','return.5000','return.10000','return.30000'))

# paste("bucketcor(df[df$type == 1], \"abs.balance_5\", \"balance_5\", c('return.1000','return.5000','return.10000','return.30000'))")
# bucketcor(df[df$type == 1], "abs.balance_5", "balance_5", c('return.1000','return.5000','return.10000','return.30000'))

# paste("bucketcor(df[df$type == 2], \"abs.balance_5\", \"balance_5\", c('return.1000','return.5000','return.10000','return.30000'))")
# bucketcor(df[df$type == 2], "abs.balance_5", "balance_5", c('return.1000','return.5000','return.10000','return.30000'))


