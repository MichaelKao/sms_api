import re

response_messages = {
    '0000': '成功',
    '1186': '請輸入帳號密碼',
    '1207': '請使用陣列傳送電話號碼',
    '1212': '請輸入傳輸的電話號碼',
    '1218': '請輸入傳輸的短碼',
    '1233': '帳號密碼錯誤',
    '1247': '短碼無效',
    '1267': '欲傳送數量超過可使用額度,請先儲值後再進行傳送!',
    '1273': '字數超過上限，中文(含中英文混和)70字，英文160字',
    '1274': '字數超過上限，中文(含中英文混和)330字，英文760字',
    '1299': '參數不足',
}

# 根據回傳代碼獲取訊息
def get_response_message(code):
    return response_messages.get(str(code), '未知錯誤')

# DR 回傳代碼對應的訊息
delivery_status = {
    '000': 'DELIVRD',  # 成功送達
    '001': 'EXPIRED',  # 已過期
    '999': 'UNDELIVERABL'  # 無法送達
}

# 根據 DR 回傳代碼獲取送達狀態
def get_delivery_status(code):
    return delivery_status.get(str(code), '未知狀態')

# 判斷訊息是否包含中文
def is_chinese(text):
    return bool(re.search(r'[\u4e00-\u9fff]', text))

# 分割訊息
def split_message(msg, max_length):
    return [msg[i:i+max_length] for i in range(0, len(msg), max_length)]

