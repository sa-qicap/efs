#!/usr/bin/env python
"""
Exchange names:
  "cme", "nse", "nsefno", "nsecm"

Usage on shell:
  python ./trading_cal.py -e nse -m next -d 20171222
  python ./trading_cal.py -e nse -m prev -d 20171226
  python ./trading_cal.py -e cme -m prev -d 20171226
  python ./trading_cal.py -e nse -m is_holiday -d 20171225
  python ./trading_cal.py -e nse -m is_holiday -d 20171019 --special_is_holiday

In code:
  import trading_cal
  import datetime

  output_date = trading_cal.get_next_trade_datestring("nse", "2017_12_22", dateformat="%Y_%m_%d")
  output_date = trading_cal.get_prev_trade_datestring("nse", "20171226")

  is_holiday = trading_cal.is_holiday("nse", "20171225")
  is_holiday = trading_cal.is_holiday("nse", "2017_12_25", dateformat="%Y_%m_%d")
"""

import sys
import datetime
import argparse


NSE_SPECIAL_DAYS = [
    # Trading is done if it is holiday
    "20151111",
    "20161030",
    "20171019",
    "20181107",
    "20191027",
    "20200303", # Disaster recovery
    "20201114",
    "20211104",
    "20221024",
    "20231112",
    "20240120",
    "20240302",
    "20241101",
    "20240518",
]


NSE_FORCE_NO_HOLIDAY = [
    "20200201",
    "20240120",
    "20240518",
]


NSE_HOLIDAYS = [
    "sat",
    "sun",
    # 2015
    "20150126",
    "20150217",
    "20150306",
    "20150402",
    "20150403",
    "20150414",
    "20150501",
    "20150917",
    "20150925",
    "20151002",
    "20151022",
    "20151112",
    "20151125",
    "20151225",
    # 2016
    "20160126",
    "20160307",
    "20160324",
    "20160325",
    "20160414",
    "20160415",
    "20160419",
    "20160706",
    "20160815",
    "20160905",
    "20160913",
    "20161011",
    "20161012",
    "20161031",
    "20161114",
    # 2017
    "20170126",
    "20170224",
    "20170313",
    "20170404",
    "20170414",
    "20170501",
    "20170626",
    "20170815",
    "20170825",
    "20171002",
    "20171020",
    "20171225",
    # 2018
    "20180126",
    "20180213",
    "20180302",
    "20180329",
    "20180330",
    "20180501",
    "20180815",
    "20180822",
    "20180913",
    "20180920",
    "20181002",
    "20181018",
    "20181108",
    "20181123",
    "20181225",
    # 2019
    "20190304",
    "20190321",
    "20190417",
    "20190419",
    "20190429", # General Elections
    "20190501",
    "20190605",
    "20190812",
    "20190815",
    "20190902",
    "20190910",
    "20191002",
    "20191008",
    "20191021", # Assembly Elections
    "20191028",
    "20191112",
    "20191225",
    # 2020
    "20200221",
    "20200310",
    "20200402",
    "20200406",
    "20200410",
    "20200414",
    "20200501",
    "20200525",
    "20201002",
    # "20201114", - muhurat trading
    "20201116",
    "20201130",
    "20201225",
    # 2021
    "20210126",
    "20210311",
    "20210329",
    "20210402",
    "20210414",
    "20210421",
    "20210513",
    "20210721",
    "20210819",
    "20210910",
    "20211015",
    "20211105",
    "20211119",
    #"20211104",  - muhurat trading
    # 2022
    "20220126",
    "20220301",
    "20220318",
    "20220414",
    "20220415",
    "20220503",
    "20220809",
    "20220815",
    "20220831",
    "20221005",
    "20221026",
    "20221108",
    #"20221024", -- muhurat trading
    #2023
    "20230126",
    "20230307",
    "20230330",
    "20230404",
    "20230407",
    "20230414",
    "20230501",
    "20230629",
    "20230815",
    "20230919",
    "20231002",
    "20231024",
    "20231114",
    "20231127",
    #"20231112",  - muhurat trading
    "20231225",
    #2024
    "20240122",
    "20240126",
    "20240308",
    "20240325",
    "20240329",
    "20240411",
    "20240417",
    "20240501",
    "20240520",
    "20240617",
    "20240717",
    "20240815",
    "20241002",
    #"20241101",  - muhurat trading
    "20241115",
    "20241225",
]


NSECDS_HOLIDAYS = [
    "sat",
    "sun",
    # 2019
    "20190219",
    "20190304",
    "20190321",
    "20190401",
    "20190417",
    "20190419",
    "20190429", # General Elections
    "20190501",
    "20190605",
    "20190812",
    "20190815",
    "20190902",
    "20190910",
    "20191002",
    "20191008",
    "20191021", # Assembly Elections
    # "20191027", - muhurat trading
    "20191028",
    "20191112",
    "20191225",
    # 2020
    "20200219",
    "20200221",
    "20200310",
    "20200325",
    "20200401",
    "20200402",
    "20200406",
    "20200410",
    "20200414",
    "20200501",
    "20200507",
    "20200525",
    "20201002",
    # "20201114", - muhurat trading
    "20201030",
    "20201116",
    "20201130",
    "20201225",
    # 2021
    "20210126",
    "20210219",
    "20210311",
    "20210329",
    "20210401",
    "20210402",
    "20210413",
    "20210414",
    "20210421",
    "20210513",
    "20210526",
    "20210721",
    "20210816",
    "20210819",
    "20210910",
    "20211015",
    "20211019",
    #"20211104", - muhurat trading
    "20211105",
    "20211119",
    #2023
    "20230126",
    "20230307",
    "20230322",
    "20230330",
    "20230404",
    "20230407",
    "20230414",
    "20230501",
    "20230505",
    "20230128",
    "20230815",
    "20230816",
    "20230919",
    "20230928",
    "20231002",
    "20231024",
    "20231114",
    #"20231112",  - muhurat trading
    "20231127",	
    "20231225",
]


CME_HOLIDAYS = ["sat", "sun"]


BSECM_SPECIAL_DAYS = [
    "20191027",
    "20201114",
]


BSECM_HOLIDAYS = [
    "sat",
    "sun",
    # 2016
    "20160126",
    "20160307",
    "20160324",
    "20160325",
    "20160414",
    "20160415",
    "20160419",
    "20160706",
    "20160815",
    "20160905",
    "20160913",
    "20161011",
    "20161012",
    "20161031",
    "20161114",
    # 2017
    "20170126",
    "20170224",
    "20170313",
    "20170404",
    "20170414",
    "20170501",
    "20170626",
    "20170815",
    "20170825",
    "20171002",
    # "20171019", - muhurat trading
    "20171020",
    "20171225",
    # 2018
    "20180126",
    "20180213",
    "20180302",
    "20180329",
    "20180330",
    "20180501",
    "20180815",
    "20180822",
    "20180913",
    "20180920",
    "20181002",
    "20181018",
    # "20181107", - muhurat trading
    "20181108",
    "20181123",
    "20181225",
    # 2019
    "20190304",
    "20190321",
    "20190417",
    "20190419",
    "20190429", # General Elections
    "20190501",
    "20190605",
    "20190812",
    "20190815",
    "20190902",
    "20190910",
    "20191002",
    "20191008",
    "20191021", # Assembly Elections
    # "20191027", - muhurat trading
    "20191028",
    "20191112",
    "20191225",
    # 2020
    "20200221",
    "20200310",
    "20200402",
    "20200406",
    "20200410",
    "20200414",
    "20200501",
    "20200525",
    "20201002",
    # "20201114", - muhurat trading
    "20201116",
    "20201130",
    "20201225",
    #2024
    "20240126",
    "20240308",
    "20240325",
    "20240329",
    "20240411",
    "20240417",
    "20240501",
    "20240617",
    "20240717",
    "20240815",
    "20241002",
    "20241101",
    "20241115",
    "20241222",
    "20241226",
]

B3_SPECIAL_DAYS = [
]


B3_HOLIDAYS = [
    "sat",
    "sun",
    # 2019
    "20190101",
    "20190125",
    "20190304",
    "20190305",
    "20190419",
    "20190501",
    "20190620",
    "20191115",
    "20191120",
    "20191224",
    "20191225",
    "20191231",
    # 2020
    "20200101",
    "20200224",
    "20200225",
    "20200305",
    "20200325",
    "20200410",
    "20200421",
    "20200501",
    "20200611",
    "20200907",
    "20201012",
    "20201102",
    "20201224",
    "20201225",
    "20201231",
    # 2021
    "20210101",
    "20210125",
    "20210215",
    "20210216",
    "20210402",
    "20210421",
    "20210603",
    "20210709",
    "20210907",
    "20211012",
    "20211102",
    "20211115",
    "20211224",
    "20211231",
    # 2022
    "20220101",
    "20220228",
    "20220301",
    "20220415",
    "20220421",
    "20220616",
    "20220907",
    "20221012",
    "20221102",
    "20221115",
    "20221230",
    #2023
    "20230125",
    "20230220",
    "20230221",
    "20230407",
    "20230421",
    "20230501",
    "20230608",
    "20230709",
    "20230810",
    "20230907",
    "20231012",
    "20231102",
    "20231115",
    "20231225",
    "20231229",
]


def is_holiday(exchange, inp_dt, dateformat="%Y%m%d", special_is_holiday=False):
    if isinstance(inp_dt, datetime.datetime) or isinstance(inp_dt, datetime.date):
        exch_dt = inp_dt
    elif isinstance(inp_dt, str):
        exch_dt = datetime.datetime.strptime(inp_dt, dateformat)
    else:
        print(type(inp_dt))
        assert False

    force_no_holiday = []
    if exchange.upper() == "CME":
        special_days = []
        holidays = CME_HOLIDAYS
    elif exchange.upper() in ["NSEFNO", "NSECM", "NSE"]:
        special_days = NSE_SPECIAL_DAYS
        holidays = NSE_HOLIDAYS
        force_no_holiday = NSE_FORCE_NO_HOLIDAY
    elif exchange.upper() in ["NSECDS"]:
        special_days = NSE_SPECIAL_DAYS
        holidays = NSECDS_HOLIDAYS
    elif exchange.upper() in ["BSECM"]:
        special_days = BSECM_SPECIAL_DAYS
        holidays = BSECM_HOLIDAYS
    elif exchange.upper() in ["B3"]:
        special_days = B3_SPECIAL_DAYS
        holidays = B3_HOLIDAYS
    else:
        print("Unknown exchange")
        assert False

    cur_ds = exch_dt.strftime("%Y%m%d")

    if cur_ds in force_no_holiday:
        return False

    if cur_ds in special_days:
        return special_is_holiday

    if cur_ds in holidays:
        return True

    # Check for sat/sun/mon/etc..
    if exch_dt.strftime("%a").lower()[0:3] in holidays:
        return True

    return False


def get_trade_datestring(exchange, inp_datestring,
                         dateformat="%Y%m%d", timedelta=1):
    inp_dt = datetime.datetime.strptime(inp_datestring, dateformat)
    ret_dt = inp_dt
    while True:
        ret_dt = ret_dt + datetime.timedelta(days=timedelta)
        if not is_holiday(exchange, ret_dt):
            return ret_dt.strftime(dateformat)


def get_next_trade_datestring(exchange, inp_datestring, dateformat="%Y%m%d"):
    return get_trade_datestring(
        exchange, inp_datestring, dateformat=dateformat, timedelta=1)


def get_prev_trade_datestring(exchange, inp_datestring, dateformat="%Y%m%d"):
    return get_trade_datestring(
        exchange, inp_datestring, dateformat=dateformat, timedelta=-1)


def main():
    # Example usage:
    parser = argparse.ArgumentParser(description="Trading calendar")
    parser.add_argument(
        "-m",
        "--mode",
        dest="mode",
        choices=["prev", "next", "is_holiday", "test"],
        type=str.lower,
        default="prev",
        help="Mode. Default: 'prev'"
    )
    parser.add_argument(
        "--special_is_holiday",
        dest="special_is_holiday",
        action="store_true",
        help="Consider special days as holidays",
        default=False
    )
    parser.add_argument(
        "-e",
        "--exchange",
        dest="exchange",
        choices=["nsecm", "nsefno", "cme", "nse", "nsecds", "b3"],
        type=str.lower,
        default="nse",
        help="Exchange name. Default: 'nse'"
    )
    parser.add_argument(
        "-d",
        "--date",
        dest="date",
        type=str,
        help="Input date: default in '%%Y%%m%%d'. Override using -f",
        required=True
    )
    parser.add_argument(
        "-f",
        "--format",
        dest="dateformat",
        type=str,
        help="Output date will use same format. Default: '%%Y%%m%%d'",
        default="%Y%m%d"
    )

    myargs = parser.parse_args()

    if myargs.mode == "test":
        print(get_prev_trade_datestring("CME", "20180129"))
        print(get_next_trade_datestring("NSEFNO", "20180129"))
        print(get_prev_trade_datestring("NSEFNO", "20180129"))
        print(get_next_trade_datestring("NSECM", "20180129"))
        print(get_prev_trade_datestring("NSECM", "20180129"))
        print(get_next_trade_datestring("NSECDS", "20190129"))
        print(get_prev_trade_datestring("NSECDS", "20190129"))
        print(is_holiday("cme",
                         datetime.datetime.strptime("20171225", "%Y%m%d")))
        print(is_holiday("nse",
                         datetime.datetime.strptime("20171225", "%Y%m%d")))
        print(is_holiday("nse", "20171225"))
        print(is_holiday("nse", "2017_12_25", dateformat="%Y_%m_%d"))
        return 0
    elif myargs.mode == "next":
        print(get_next_trade_datestring(
            myargs.exchange, myargs.date, myargs.dateformat))
        return 0
    elif myargs.mode == "prev":
        print(get_prev_trade_datestring(
            myargs.exchange, myargs.date, myargs.dateformat))
        return 0
    elif myargs.mode == "is_holiday":
        ret_val = is_holiday(
            myargs.exchange,
            datetime.datetime.strptime(myargs.date, myargs.dateformat),
            special_is_holiday=myargs.special_is_holiday)
        print(ret_val)
        if ret_val:
            return 0
        else:
            return -1
    else:
        return -1


if __name__ == "__main__":
    sys.exit(main())
