# service.py
import threading
from utils.helpers import is_chinese, split_message
import requests
from utils.rabbitmq_utils import RabbitMQUtils
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from models.sms_request import SmsRequest

# 從環境變數中讀取資料庫連接字串
# DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://tlgrdcb2bAp:27938888@py-db-1:5432/TLGRDCB2BSIT")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://tlgrdcb2bAp:27938888@localhost:5432/TLGRDCB2BSIT")

# 設置 SQLAlchemy 引擎
engine = create_engine(DATABASE_URL)

# 創建 Base 類
Base = declarative_base()

# 創建 Session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 用於存儲每個用戶的連接數
user_connections = {}
user_connections_lock = threading.Lock()
# 最大連接數
MAX_CONNECTIONS = 5
# 每個交易最多支持的電話號碼數量
MAX_NUMBERS_PER_REQUEST = 1000
    
class SmsService:
    def __init__(self):
        # 初始化 RabbitMQ 工具類
        self.rabbitmq_util = RabbitMQUtils()

    # 發送簡訊
    def send_sms(self, data):
        try:
            # 創建資料庫連線
            db = SessionLocal()
            # 將收到的數據映射到 ORM 模型
            sms_request = SmsRequest(
                acc=data['acc'],
                pas=data['pas'],
                subacc=data.get('subacc', None),
                from_=data['from'],
                msg=data['msg'],
                to_=data['To'],
                expire_time=data.get('expiretime', 86400),
                retry=data.get('retry', 'Y'),
                auto_split=data.get('autosplit', 'N'),
                priority=data.get('priority', 0)
            )
            # 添加並提交到資料庫
            db.add(sms_request)
            
            db.commit()
        except Exception as e:
            db.rollback()  # 回滚事务
            return {'code': '123', 'task_id': ''}
        finally:
            db.close()  # 关闭会话
        try:
            # 從 data 中獲取 acc
            acc = data.get('acc')
		    # 呼叫 check_request 函數檢查參數有效性
            result = check_request(data)
            if result is not None:
                return result
			# 使用鎖來確保操作的原子性
            with user_connections_lock:
			    # 檢查該用戶當前的連接數
                current_connections = user_connections.get(acc, 0)
			    # 如果當前連接數超過最大限制，拒絕新的連線
                if current_connections >= MAX_CONNECTIONS:
                   return {'code': '429', 'task_id': ''}
			    # 增加該用戶的連接數
                user_connections[acc] = current_connections + 1
		    # 設定 headers，將 Content-Type 設為 application/x-www-form-urlencoded
            headers = {
			    'Content-Type': 'application/x-www-form-urlencoded'
		    }
		    # 組裝傳送到外部 API 的資料
            payload = {
			    'acc': acc,
			    'pas': data.get('pas'),
			    'subacc': data.get('subacc'),
			    'from': data.get('from'),
			    'msg': data.get('msg'),
			    'To': data.get('To'),
		    }
            # 編碼 payload 的內容為 ISO-8859-1
            payload = {key: value.encode('ISO-8859-1') if isinstance(value, str) else value for key, value in payload.items()}
		    # 發送 POST 請求到外部 API
            response = requests.post("https://smsxxx.tscmc.com.tw/sms/api2/TSMT", data=payload, headers=headers)
		    # 檢查外部 API 的回應
            if response.status_code == 200:
                result = response.json()  # 假設回應為 JSON 格式
                code = str(result.get('code'))
			    # 處理完請求後，減少該用戶的連接數
                with user_connections_lock:
                    user_connections[acc] -= 1  # 減少該用戶的連接數
                    
                    
                    # 發送消息到 RabbitMQ
                    #self.rabbitmq_util.send_message(payload)
                    
                    return {'code': code, 'task_id': result.get('task_id')}
            else:
                return {'code': response.status_code, 'task_id': ''}
        except Exception as e:
		    # 發生錯誤時，回傳錯誤訊息
            return {'code': '500', 'task_id': ''}
        finally:
            # 無論請求結果如何，減少用戶的連接數
            if acc:
                with user_connections_lock:
                    # 確保 acc 存在於字典中，再進行減少操作
                    if acc in user_connections:
                        user_connections[acc] -= 1  # 減少該用戶的連接數
                        # 如果連接數為0，可以選擇從字典中移除該條目
                        if user_connections[acc] == 0:
                            del user_connections[acc]

    # 接收即時 DR 狀態更新
    def receive_dr_status(self, data):
        try:
            # 從請求中獲取參數
            task_id = data.get('task_id')
            msg_id = data.get('msg_id')
            status = data.get('status')
            # 檢查必需參數
            if not task_id or not msg_id or not status:
                return {'code': '2'}
            headers = {
			    'Content-Type': 'application/x-www-form-urlencoded'
		    }
            # 組裝傳送到外部 API 的資料
            payload = {
			    'task_id': task_id,
			    'msg_id': msg_id,
			    'status': status,
		    }
            # 編碼 payload 的內容為 ISO-8859-1
            payload = {key: value.encode('ISO-8859-1') if isinstance(value, str) else value for key, value in payload.items()}
            # 發送 POST 請求到外部 API
            response = requests.post("https://smsxxx.tscmc.com.tw/sms/api2/???", data=payload, headers=headers)
            # 返回結果
            if response.status_code == 200:
                return {'code': '1'}
            else:
                return {'code': '2'}
        except Exception as e:
            return {'code': '2'}

    # 接收即時 MO 簡訊通知
    def mo_notice(self, data):
        try:
            # 從請求中獲取參數
            form = data.get('From')
            msg = data.get('Msg').encode('utf-8')
            to = data.get('To')
            msg_id = data.get('msg_id')
            # 檢查必需參數
            if not data or not form or not msg or not to or not msg_id:
                return {'code': '2'}
            headers = {
			    'Content-Type': 'application/x-www-form-urlencoded'
		    }
            # 組裝傳送到外部 API 的資料
            payload = {
			    'form': form,
			    'msg': msg,
			    'to': to,
                'msg_id': msg_id,
		    }
            # 編碼 payload 的內容為 ISO-8859-1
            payload = {key: value.encode('ISO-8859-1') if isinstance(value, str) else value for key, value in payload.items()}
            # 發送 POST 請求到外部 API
            response = requests.post("https://smsxxx.tscmc.com.tw/sms/api2/???", data=payload, headers=headers)
            # 返回結果
            if response.status_code == 200:
                return {'code': '1'}
            else:
                return {'code': '2'}
        except Exception as e:
            return {'code': '2'}

def check_request(data):
    # 帳號
    acc = data['acc'] 
    # 密碼
    pas = data['pas']
    # 子帳號(CDR分帳用)
    subacc = data.get('subacc', None)
    # 指定發訊方號碼
    data_from = data['from']
    # 訊息內容(請傳UTF8編碼,中文(含中英混和)限制在70個字,英文限制在160個字)。
    msg = data['msg']
    # 收訊者門號,可使用陣列一次發送多筆簡訊,請使用陣列傳送號碼(每個交易不得超過1000筆)。
    to = data['To']
    # 是否啟用長簡訊
    autosplit = data.get('autosplit', 'N')
    # 參數不足
    if not acc or not pas or not data_from or not msg or not to:
        return {'code': '1299', 'task_id': ''}
    # 帳號密碼為空
    if not acc or not pas:
        return {'code': '1186', 'task_id': ''}
    # 發訊方號碼為空
    if not data_from:
        return {'code': '1212', 'task_id': ''}
    # 檢查收訊者門號是否為陣列，並且每個電話號碼都有效
    if not to or not isinstance(to, list):
        return {'code': '1207', 'task_id': ''}
    # 檢查電話號碼數量是否超過1000筆
    if len(to) > MAX_NUMBERS_PER_REQUEST:
        return {'code': '1267', 'task_id': ''}
    # 處理長簡訊邏輯
    if autosplit == 'Y':  # 啟用長簡訊分割
        if is_chinese(msg):  # 如果訊息包含中文
            if len(msg) > 330:  # 如果超過中文長簡訊字數上限
                msg_parts = split_message(msg, 70)  # 將訊息分割為最多5則
                if len(msg_parts) > 5:  # 最多分割為5則簡訊
                    data['msg'] = msg_parts
                    return {'code': '1274', 'task_id': ''}
        else:  # 假設全為英文
            if len(msg) > 760:  # 如果超過英文長簡訊字數上限
                msg_parts = split_message(msg, 160)  # 將訊息分割為最多5則
                if len(msg_parts) > 5:  # 最多分割為5則簡訊
                    data['msg'] = msg_parts
                    return {'code': '1274', 'task_id': ''}
    else:  # 沒有啟用長簡訊分割
        if is_chinese(msg):  # 如果訊息包含中文
            if len(msg) > 70:  # 超過中文訊息字數上限
                return {'code': '1273', 'task_id': ''}
        else:  # 假設全為英文
            if len(msg) > 160:  # 超過英文訊息字數上限
                return {'code': '1273', 'task_id': ''}
    return

