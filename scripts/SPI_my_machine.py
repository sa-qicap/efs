import os
import sys
from datetime import datetime, timedelta
import pandas as pd
import trading_cal

def iisl_location(date, underlying_folder_name):
    if date <= "20211006":
      return "/global/data/reference_data/IISL/NSEFNO/" + underlying_folder_name + "_" + date + ".zip"
    else:
      return "/global/data/reference_data/IISL/NSEFNO/" + date + "/" + underlying_folder_name + "_" + date +".zip"

def calculateSpi(indexTsFilePath, indexBodFilePath, indexLotSize):
    indexTsFile = pd.read_csv(indexTsFilePath)
    indexBodFile = pd.read_csv(indexBodFilePath)
    indexLastClosing = indexTsFile.iloc[0]['CLOSE_PRICE']
    indexMarketCap = indexTsFile.iloc[0]['INDEX_MKT_CAP']
    indexBodFile['MarketCapClosing'] = indexBodFile['ADJ_CLOSE_PRICE']*indexBodFile['ISSUE_CAP']*indexBodFile['INVESTIBLE_FACTOR']*indexBodFile['CAP_FACTOR']
    indexMarketCap_usingSum = indexBodFile['MarketCapClosing'].sum()
    indexBodFile['WeightCalculated'] = indexBodFile['MarketCapClosing']/indexMarketCap_usingSum
    indexBodFile['Spi'] = indexLastClosing*indexBodFile['WeightCalculated']/indexBodFile['ADJ_CLOSE_PRICE']
    indexBodFile['StocksPerIndexLot'] = indexBodFile['Spi'] * indexLotSize
    return indexBodFile

def parse_index_cm_contracts_from_date(sdate, underlying):
  if underlying == "BANKNIFTY":
    underlying_folder_name = "NIFTY_BANK"
  elif underlying == "FINNIFTY":
    underlying_folder_name = "NIFTY_FINANCIAL_SERVICES"
  elif underlying == "NIFTY":
    underlying_folder_name = "NIFTY_50"
  elif underlying == "MIDCPNIFTY":
    underlying_folder_name = "NIFTY_MIDCAP_SELECT"
  else:
    print("underlying not handled")
  
  prev_date = trading_cal.get_prev_trade_datestring("nse", sdate, dateformat="%Y%m%d")

  index_bod_file = '/efs/sameer.arora/historical_index_data/' + underlying_folder_name + '/bod' + sdate + '.csv'

  if (not os.path.isfile(index_bod_file)):
    cmd1 = "unzip -o "+iisl_location(prev_date, underlying_folder_name)+" -d "+ "/efs/sameer.arora/historical_index_data/"+underlying_folder_name+"/"
    print(cmd1)
    os.system(cmd1)

  index_bod_file = '/efs/sameer.arora/historical_index_data/' + underlying_folder_name + '/bod' + sdate + '.csv'
  index_ts_file = '/efs/sameer.arora/historical_index_data/' + underlying_folder_name + '/ts' + prev_date + '.csv'
  new_FNO_path = '/global/data/reference_data/contract_data/NSEFNO/'+sdate+'-NSEFNO-CONTRACTMASTER.csv'
  new_CM_path = '/global/data/reference_data/contract_data/NSECM/'+sdate+'-NSECM-CONTRACTMASTER.csv'

  df_fno = pd.read_csv(new_FNO_path, sep='|')
  lot_size = df_fno[(df_fno["nse_symbol"]==underlying) & (df_fno["contract_type"]=="FUT")]['lotsize'].values[0]
  new_bod_file = calculateSpi(index_ts_file, index_bod_file, lot_size)
  
  df_cm = pd.read_csv(new_CM_path, sep='|')

  df_cm["SYMBOL"] = df_cm["primary_contract_name"]
  df_cm['token'] = df_cm['venue_token']
  new_bod_file = new_bod_file.merge(df_cm[['token','SYMBOL']], on='SYMBOL')
  # new_bod_file.to_csv(dir+"/config/SPI"+underlying+".csv", index=False)
  return new_bod_file

def get_bod_im_ts_file_path(sdate, underlying):
  if underlying == "BANKNIFTY":
    underlying_folder_name = "NIFTY_BANK"
  elif underlying == "FINNIFTY":
    underlying_folder_name = "NIFTY_FINANCIAL_SERVICES"
  elif underlying == "NIFTY":
    underlying_folder_name = "NIFTY_50"
  elif underlying == "MIDCPNIFTY":
    underlying_folder_name = "NIFTY_MIDCAP_SELECT"
  else:
    print("underlying not handled")
  
  prev_date = trading_cal.get_prev_trade_datestring("nse", sdate, dateformat="%Y%m%d")

  index_bod_file = '/efs/sameer.arora/historical_index_data/' + underlying_folder_name + '/bod' + sdate + '.csv'

  if (not os.path.isfile(index_bod_file)):
    cmd1 = "unzip -o "+iisl_location(prev_date, underlying_folder_name)+" -d "+ "/efs/sameer.arora/historical_index_data/"+underlying_folder_name+"/"
    print(cmd1)
    os.system(cmd1)

  index_bod_file = '/efs/sameer.arora/historical_index_data/' + underlying_folder_name + '/bod' + sdate + '.csv'
  index_ts_file = '/efs/sameer.arora/historical_index_data/' + underlying_folder_name + '/ts' + prev_date + '.csv'
  index_im_file = '/efs/sameer.arora/historical_index_data/' + underlying_folder_name + '/im' + prev_date + '.csv'

  return index_bod_file, index_im_file, index_ts_file
  