import requests
import json
import time
import datetime
import pandas as pd

start_unix_time = str(1400630400)  # 21/05/2014
end_unix_time = str(int(time.time()))  # Current Date
token_list = ["btc", "eth", "ltc", "xmr"]


# Use only "btc", "xmr", "ltc", "eth"
def get_support_data(token):
    support_data = \
        json.loads(requests.get('https://coinmetrics.io/api/v1/get_available_data_types_for_asset/' + token).text)[
            "result"]
    return support_data


def common_elements(list1, list2):
    return [element for element in list1 if element in list2]


# get common elements of btc, xmr, ltc, eth
def get_common_support_data():
    temp = common_elements(get_support_data("btc"), get_support_data("xmr"))
    temp = common_elements(temp, get_support_data("ltc"))
    common_support_data = common_elements(temp, get_support_data("eth"))
    return common_support_data


def get_asset_data_for_time_range(asset, data_type):
    request_response = (json.loads(requests.get(
        "https://coinmetrics.io/api/v1/get_asset_data_for_time_range/"
        + asset + "/" + data_type + "/" + start_unix_time + "/" + end_unix_time).text))
    request_response = request_response["result"]
    for key in request_response:
        key[0] = datetime.datetime.fromtimestamp(key[0]).strftime('%Y-%m-%d')
    request_response = pd.DataFrame.from_dict(request_response)
    request_response.columns = ["Date", str(data_type)]
    request_response.set_index("Date", inplace=True)
    request_response.index = pd.DatetimeIndex(request_response.index)
    return request_response


common_support_data = get_common_support_data()

for token in token_list:
    temp_df = get_asset_data_for_time_range(token, "fees")
    temp_df = temp_df.drop(columns="fees")

    for common_support_datum in common_support_data:
        temp = pd.merge(temp_df, get_asset_data_for_time_range(token, str(common_support_datum)), on="Date")

    temp_df.to_csv(token + ".csv")
