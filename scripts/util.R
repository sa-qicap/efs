adjcor=function(x,y){
mean(x*y)/(sd(x)*sd(y))
}

column1d=function(df,col,fun){
aggregate(df[,!names(df) %in% col],by=list(df[[col]]),FUN=fun)


}

first =function(x){
x[1]
}
last =function(x){
x[length(x)]
}

maxel1 = function(x){
if(length(x)==1) {
 return( -1)
 }else{

 return(max(x[-1]))
 }


}
meanel1 = function(x){
if(length(x)==1) {
 return( -1)
 }else{

 return(mean(x[-1]))
 }
trimQuant = function(x){

return(quantile(x,0.99))

}

}
columncor=function(df,col,x,y)
{
ddply(df,col,function(d)cor(d[,x],d[,y]))
}

columnadjcor=function(df,col,x,y)
{
ddply(df,col,function(d)adjcor(d[,x],d[,y]))
}

bucket1d=function(df,col,fun="mean",numBuckets=5){
split = 1/numBuckets
breaks = quantile(df[[col]],seq(0,1,split))
#lab = as.character(seq(1,length(breaks)-1,1))
lab = as.character(breaks[-1])
df1 = transform(df,group = cut(df[[col]],breaks=breaks,labels = lab,include.lowest = TRUE))
df1 = df1[!is.na(df1$group),]
df2=aggregate(df1,by = list(df1$group),FUN=fun)
df1$count=1
x=aggregate(df1$count,by = list(df1$group),FUN=sum)
colnames(x)[2]='count'
df2=merge(df2,x,by='Group.1')
colnames(df2)[1]="bucket"
df2[order(df2$bucket),]
}


bucketcor=function(df,col,x,y,numBuckets=5){
split = 1/numBuckets
breaks = unique(quantile(df[[col]],seq(0,1,split)))
#lab = as.character(seq(1,length(breaks)-1,1))
if (length(breaks) < 3) {
  warning(paste("Insufficient unique breaks to create meaningful buckets for column:", col))
  return(NULL)
}
lab = as.character(breaks[-1])
df1 = transform(df,group = cut(df[[col]],breaks=breaks,labels = lab))
df1 = df1[!is.na(df1$group),]
df2=ddply(df1,"group",function(data)cor(data[,x],data[,y]))
#colnames(df2)[1]="bucket"
df2
}

bucketcor_range <- function(df, col, x, y, numBuckets = 5) {
  # Calculate the minimum and maximum values of the specified column
  min_col <- min(df[[col]], na.rm = TRUE)
  max_col <- max(df[[col]], na.rm = TRUE)
  
  # Create breaks that divide the range into equal intervals
  breaks <- seq(min_col, max_col, length.out = numBuckets + 1)
  
  # Check if there are enough unique breaks to form buckets
  if (length(unique(breaks)) < 3) {
    warning(paste("Insufficient unique breaks to create meaningful buckets for column:", col))
    return(NULL)
  }
  
  # Define labels for the buckets
  lab <- as.character(breaks[-1])
  
  # Assign each observation to a bucket based on the breaks
  df1 <- transform(df, group = cut(df[[col]], breaks = breaks, labels = lab, include.lowest = TRUE))
  
  # Remove any rows with NA in the group
  df1 <- df1[!is.na(df1$group), ]
  
  # Calculate the correlation between x and y within each bucket
  df2=ddply(df1,"group",function(data)cor(data[,x],data[,y]))
  
  # Return the dataframe with correlations
  df2
}


getGroupedDf = function(df, column_name,numBuckets = 5) {
    print("creating absolute column")
  # Check if column exists in dataframe
  if (column_name %in% colnames(df)) {
      # Create absolute column
      df[, paste("abs.", column_name, sep = "") := abs(get(column_name))]
  } else {
      stop("Column not found in dataframe.")
  }

  col = paste("abs.", column_name, sep = "")

  split = 1 / numBuckets
  breaks = unique(quantile(df[[col]], seq(0, 1, split)))
  if (length(breaks) < 3) {
    warning(paste("Insufficient unique breaks to create meaningful buckets for column:", col))
    return(NULL)
  }
  lab = as.character(breaks[-1])
  df1 = transform(df, group = cut(df[[col]], breaks = breaks, labels = lab))
  df1 = df1[!is.na(df1$group), ]
  df1
}

# bucketcor for 2 columns

bucketcor2 <- function(df, col1, col2, x, y, numBuckets = 5) {
  split <- 1 / numBuckets
  # Calculate breaks for col1
  breaks1 <- quantile(df[[col1]], probs = seq(0, 1, split), na.rm = TRUE)
  if (length(unique(breaks1)) < 2) {
    warning(paste("Insufficient unique breaks to create meaningful buckets for column:", col1))
    return(NULL)
  }
  # Assign group1 based on breaks1
  df$group1 <- cut(df[[col1]], breaks = breaks1, include.lowest = TRUE)
  df <- df[!is.na(df$group1), ]
  
  # Within each group1, calculate breaks for col2 and assign group2
  df <- ddply(df, .(group1), function(subdf) {
    breaks2 <- quantile(subdf[[col2]], probs = seq(0, 1, split), na.rm = TRUE)
    if (length(unique(breaks2)) < 2) {
      warning(paste("Insufficient unique breaks to create meaningful buckets for column:", col2, "within group1:", unique(subdf$group1)))
      subdf$group2 <- NA
    } else {
      subdf$group2 <- cut(subdf[[col2]], breaks = breaks2, include.lowest = TRUE)
    }
    return(subdf)
  })
  
  # Remove rows with NA in group2
  df <- df[!is.na(df$group2), ]
  
  # Compute correlations within each combination of group1 and group2
  df2 <- ddply(df, .(group1, group2), function(data) {
    # Ensure there are at least two observations to compute correlation
    if (nrow(data) < 2) {
      return(data.frame(cor = NA))
    } else {
      correlation <- cor(data[[x]], data[[y]], use = "complete.obs")
      return(data.frame(cor = correlation))
    }
  })
  
  return(df2)
}






bucketadjcor=function(df,col,x,y,numBuckets=5){
split = 1/numBuckets
breaks = quantile(df[[col]],seq(0,1,split))

#lab = as.character(seq(1,length(breaks)-1,1))
lab = as.character(breaks[-1])
df1 = transform(df,group = cut(df[[col]],breaks=breaks,labels = lab))
df1 = df1[!is.na(df1$group),]
df2=ddply(df1,"group",function(data)adjcor(data[,x],data[,y]))
#colnames(df2)[1]="bucket"
df2
}


computeP=function(df,alpha,ret,hs,trcost){
df$pnl = sign(df[,alpha])*df[,ret]
df$p60 = pnl-df[,hs]-df[,trcost]
df
}
computePassiveP=function(df,alpha,ret,hs,trcost){
df$pnl = sign(df[,alpha])*df[,ret]
df$p60 = df$pnl+df[,hs]-df[,trcost]
#mean(df$p60)
df

}

fitLM=function(df,deps,ind,split)
{
datesall = unique(df$date)
numS = round(length(datesall)*split)
datesin = datesall[1:numS]
datesout = datesall[(numS+1):length(datesall)]
df$ins=1
#datain= data[data$date %in% datesin,]
df$ins[df$date %in% datesout]=0
str = ""
for(i in 1:length(deps)){
str=paste0(str,"+",deps[i])

}
str=paste0(ind," ~ ",str," + 0")
lms=(lm(str,data=df[df$ins==1,]))
print(summary(lms))
out = predict(lms,df)
df$res = out
df
}



sharpe= function(pnl){
16*mean(pnl)/sd(pnl)

}

calculate_range_buckets <- function(df, alpha) {
    # Calculate z-scores for the absolute values of the 'alpha' column
    abs_col <- paste("abs.", alpha, sep = "")
    df[[abs_col]] <- abs(df[[alpha]])
    df$z_score <- as.numeric(scale(df[[abs_col]]))

    # Calculate bucketcor for z-score
    print(paste("Calculating range bucketcor for alpha:", alpha))
    returns <- c('return.1000', 'return.5000', 'return.10000', 'return.30000', 'return.60000', 'return.300000', 'return.600000', 'return.900000', 'return.1800000')
    r <- bucketcor_range(df, abs_col, alpha, returns, 5)
    if (!is.null(r)) {
        print(r)
    } else {
        print(paste("No valid result for alpha:", alpha))
    }
}

calculate_buckets <- function(df, alpha) {
    # Calculate z-scores for the absolute values of the 'alpha' column
    abs_col <- paste("abs.", alpha, sep = "")
    df[[abs_col]] <- abs(df[[alpha]])
    df$z_score <- as.numeric(scale(df[[abs_col]]))

    returns <- c('return.1000', 'return.5000', 'return.10000', 'return.30000', 'return.60000', 'return.300000', 'return.600000', 'return.900000', 'return.1800000')
    df <- df %>% select(alpha, abs_col, all_of(returns), z_score)

    print("total number of points")
    print(nrow(df)) 

    # calculate bucketcor
    print(paste("Calculating bucketcor for alpha:", alpha))
    r <- bucketcor(df, abs_col, alpha, returns, 5)
    if (!is.null(r)) {
        print(r)
    } else {
        print(paste("No valid result for alpha:", alpha))
    }

    # Filter the dataframe into two parts based on z-score values
    df_gt_3 <- df[df$z_score > 3, ]
    df_le_3 <- df[df$z_score <= 3, ]


    print("total number of points with z-score <= 3")
    print(nrow(df_le_3))
    print("total number of points with z-score > 3")
    print(nrow(df_gt_3))

    # Calculate bucketcor for z-score <= 3
    print(paste("Calculating bucketcor for z-score <= 3 for alpha:", alpha))
    r1 <- bucketcor(df_le_3, abs_col, alpha, returns)
    if (!is.null(r1)) {
        print(r1)
    } else {
        print(paste("No valid result for alpha:", alpha))
    }

    # Calculate bucketcor for z-score > 3
    print(paste("Calculating bucketcor for z-score > 3 for alpha:", alpha))
    r2 <- bucketcor(df_gt_3, abs_col, alpha, returns)
    if (!is.null(r2)) {
        print(r2)
    } else {
        print(paste("No valid result for alpha:", alpha))
    }
    
}

getOneDayData <- function(df, date) {

    #extract date from log_time 
    df$date_only <- as.Date(df$log_time)

    # filter df for the given date
    df <- df[df$date_only == date, ]
    return(df)
}

getOneTime <- function(df, time) {

    return(df[df$time_only == time, ])
}

# get num points in df_gt_3 for a given alpha
getPointsGt3 <- function(df, alpha) {

    # Calculate z-scores for the absolute values of the 'alpha' column
    abs_col <- paste("abs.", alpha, sep = "")
    df[[abs_col]] <- abs(df[[alpha]])
    df$z_score <- as.numeric(scale(df[[abs_col]]))

    df_gt_3 <- df[df$z_score > 3, ]
    return(df_gt_3)
}


# get num points in df_gt_3 for a given alpha
getNumPointsGt3 <- function(df, alpha) {

    # Calculate z-scores for the absolute values of the 'alpha' column
    abs_col <- paste("abs.", alpha, sep = "")
    df[[abs_col]] <- abs(df[[alpha]])
    df$z_score <- as.numeric(scale(df[[abs_col]]))

    df_gt_3 <- df[df$z_score > 3, ]
    return(nrow(df_gt_3))
}

select_row <- function(file) {
  df <- fread(file, skip = 0, select = NULL, nrows = Inf)

  # remove rows with log time less than 2024-01-01 00:00:00
  df$log_time <- as.POSIXct(df$log_time, format = "%Y-%m-%d %H%M%OS")
  df$time_only <- format(df$log_time, format = "%H:%M:%OS")

  start_time <- "09:17:00.000000000"
  end_time <- "16:28:00.000000000"

  df <- df[df$time_only >= start_time & df$time_only <= end_time]

  # # ap > bp & bp > 0
  df <- df[df$ask > df$bid & df$bid > 0]
  df <- df[df$ask.1000 > df$bid.1000 & df$bid.1000 > 0]
  df <- df[df$ask.5000 > df$bid.5000 & df$bid.5000 > 0]
  df <- df[df$ask.10000 > df$bid.10000 & df$bid.10000 > 0]
  df <- df[df$ask.30000 > df$bid.30000 & df$bid.30000 > 0]

  return(df)
}

select_row_no_check <- function(file) {
  df <- fread(file, skip = 0, select = NULL, nrows = Inf)

  # remove rows with log time less than 2024-01-01 00:00:00
  df$log_time <- as.POSIXct(df$log_time, format = "%Y-%m-%d %H%M%OS")
  df$time_only <- format(df$log_time, format = "%H:%M:%OS")

  start_time <- "09:47:00.000000000"
  end_time <- "15:28:00.000000000"

  df <- df[df$time_only >= start_time & df$time_only <= end_time]
  return(df)
}


load_csv <- function(file) {
  df <- rbindlist(lapply(file, select_row), use.names = TRUE, fill = TRUE)
}

load_csv_no_check <- function(file) {
  df <- rbindlist(lapply(file, select_row_no_check), use.names = TRUE, fill = TRUE)
}


load_multiple_csvs_dir <- function(directories, pattern) {

  parent_directory <- directories

  # Get all directories within the parent directory
  all_directories <- list.dirs(path = parent_directory, full.names = TRUE, recursive = TRUE)
  print(all_directories)

  dir_pattern <- "2024*"

  # Use grep() to filter directories that match the pattern
  matched_directories <- grep(dir_pattern, directories, value = TRUE)
  print(matched_directories)

  # Display the matched directories
  #print(matched_directories)


  # Construct a pattern to match files that start with the given pattern
  full_pattern <- paste0("^", pattern, ".*\\.csv$")
    
  # Find all CSV files in the given directories that start with the pattern
  csv_files <- unlist(lapply(matched_directories, function(dir) {
    list.files(path = dir, pattern = full_pattern, full.names = TRUE)
  }))

  # Load and combine the data from each CSV file
  df <- rbindlist(lapply(csv_files, select_row), use.names = TRUE, fill = TRUE)
    
    return(df)
}

load_multiple_csvs <- function(dir, pattern) {
    # Construct a pattern to match files that start with the given pattern
    full_pattern <- paste0("^", pattern, ".*\\.log$")
    # print(full_pattern)
    
    csv_files <- unlist(lapply(dir, function(dir) {
    list.files(path = dir, pattern = full_pattern, full.names = TRUE)
  }))
  print(csv_files)

  df <- rbindlist(lapply(csv_files, select_row), use.names = TRUE, fill = TRUE)
    
    return(df)
}

load_multiple_csvs_no_check <- function(dir, pattern) {
    # Construct a pattern to match files that start with the given pattern
    full_pattern <- paste0("^", pattern, ".*\\.log$")
    # print(full_pattern)
    
    csv_files <- unlist(lapply(dir, function(dir) {
    list.files(path = dir, pattern = full_pattern, full.names = TRUE)
  }))
  print(csv_files)

  df <- rbindlist(lapply(csv_files, select_row_no_check), use.names = TRUE, fill = TRUE)
    
    return(df)
}

remove_cols <- function(df) {
  df <- df %>% select(-ask, -bid, -asksz, -bidsz, -ref, -bid.1000, -bidsz.1000, -ask.1000, -asksz.1000, ref.1000, -bid.5000, -bidsz.5000, -ask.5000, -asksz.5000, -ref.5000, -bid.10000, -bidsz.10000, -ask.10000, -asksz.10000, -ref.10000, -bid.30000, -bidsz.30000, -ask.30000, -asksz.30000, -ref.30000)
}


getWorstDayTime <- function(df, alpha, return) {
    # Initialize variables
    rows_diff_than_alpha <- 0
    worst_date_time <- NA
    worst_data <- NA
    worst_data_wrongs <- NA
    worst_data_rights <- NA

    df$date_only <- as.Date(df$log_time)

    # Convert `date_only` to Date format if it isn’t already
    if (!inherits(df$date_only, "Date")) {
        df$date_only <- as.Date(df$date_only)
    }

    # Convert `time_only` to character if it's not already
    if (!is.character(df$time_only)) {
        df$time_only <- as.character(df$time_only)
    }

    # Get unique days
    unique_days <- unique(df$date_only)

    # Iterate over indices
    for (i in seq_along(unique_days)) {
        day <- unique_days[i]
        day_str <- format(day, "%Y-%m-%d")
        cat('Day:', day_str, "\n")

        # Filter data for the specific day
        day_data <- df %>% filter(date_only == day)

        # Process each time for the day
        unique_times <- unique(day_data$time_only)

        for (j in seq_along(unique_times)) {
            time <- unique_times[j]
            time_str <- as.character(time)
            cat('Time:', time_str, "\n")

            # Filter data for the specific time
            time_data <- day_data %>% filter(time_only == time)

            # Calculate rows where alpha and return are mismatched
            current_rows_diff_than_alpha <- sum(
                time_data[[alpha]] * time_data[[return]] < 0,
                na.rm = TRUE
            )

            cat('Rows diff than alpha:', current_rows_diff_than_alpha, "\n")

            # Update worst date and time if a higher mismatch count is found
            if (current_rows_diff_than_alpha > rows_diff_than_alpha) {
                rows_diff_than_alpha <- current_rows_diff_than_alpha
                worst_date_time <- paste(day_str, time_str)

                worst_data_rights <- time_data[time_data[[alpha]] * time_data[[return]] >= 0, ]
                worst_data_wrongs <- time_data[time_data[[alpha]] * time_data[[return]] < 0, ]
                worst_data <- time_data
            }
        }
    }

    cat('Worst date time:', worst_date_time, "\n")
    cat("worst alpha return mismatch:", rows_diff_than_alpha, "\n")
    return(list(worst_data = worst_data, worst_data_wrongs = worst_data_wrongs, worst_data_rights = worst_data_rights))
}


library(lubridate)
getTimeAround <- function(df_small, df_big, t) {

  df$date_only <- as.Date(df$log_time)
  # Extract unique time(s) from df_small
  c_time <- unique(df_small$time_only)
  c_date <- unique(df_small$date_only)
  time_str <- as.character(c_time)
  print(time_str)
  
  # Convert the time string to POSIXct object without using hms
  time_obj <- as.POSIXct(time_str, format = "%H:%M:%S", tz = "UTC")
  
  # Calculate t seconds before and after
  time_before <- time_obj - seconds(t)
  time_after <- time_obj + seconds(t)
  
  # Format times if needed
  time_before_str <- format(time_before, "%H:%M:%S")
  time_after_str <- format(time_after, "%H:%M:%S")

     print(time_before_str)
     print(time_after_str)
  
  # Assuming you want to filter df_big based on these times
  # Convert df_big$time_only to POSIXct
  
#   # Filter df_big for times between time_before and time_after
  result <- df_big[df_big$time_only >= time_before_str & df_big$time_only <= time_after_str & df$date_only == c_date, ]
  
  return(result)
}
