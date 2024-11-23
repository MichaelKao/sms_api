-- 資料庫初始化腳本
CREATE TABLE t_sms_requests (
    trantion_no_seq BIGSERIAL PRIMARY KEY,
    acc VARCHAR(255) NOT NULL,
    pas VARCHAR(255) NOT NULL,
    subacc VARCHAR(255) DEFAULT NULL,
    "from" VARCHAR(255) NOT NULL,
    msg TEXT NOT NULL,
    "to" JSON NOT NULL,
    expire_time INT DEFAULT 86400,
    retry VARCHAR(1) DEFAULT 'Y',
    auto_split VARCHAR(1) DEFAULT 'N',
    priority INT DEFAULT 0,
    insert_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON COLUMN t_sms_requests.trantion_no_seq IS '交易編號，自動增長';
COMMENT ON COLUMN t_sms_requests.acc IS '平台帳號 (請使用貴公司在本平台的帳號)';
COMMENT ON COLUMN t_sms_requests.pas IS '平台密碼 (請使用貴公司在本平台的密碼)';
COMMENT ON COLUMN t_sms_requests.subacc IS '子帳號 (CDR分帳用，可選)';
COMMENT ON COLUMN t_sms_requests."from" IS '指定發訊方號碼 (企業短碼或長碼)';
COMMENT ON COLUMN t_sms_requests.msg IS '訊息內容 (UTF8編碼, 中文限制70字, 英文160字)';
COMMENT ON COLUMN t_sms_requests."to" IS '收訊者門號, 可使用陣列一次發送多筆簡訊';
COMMENT ON COLUMN t_sms_requests.expire_time IS '簡訊發送截止時間 (秒), 預設86400秒';
COMMENT ON COLUMN t_sms_requests.retry IS '是否開啟retry, Y啟用, N關閉 (預設為Y)';
COMMENT ON COLUMN t_sms_requests.auto_split IS '是否啟用長簡訊, N關閉(預設)或 Y啟用';
COMMENT ON COLUMN t_sms_requests.priority IS '發送優先順序, 0為標準, 1為較高 (預設為0)';
COMMENT ON COLUMN t_sms_requests.insert_date IS '資料創建時間';

-- 建立 t_dr_status 資料表
CREATE TABLE t_dr_status (
    task_id VARCHAR(255) PRIMARY KEY,
    msg_id VARCHAR(30) NOT NULL,
    status VARCHAR(50) NOT NULL,
    insert_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON COLUMN t_dr_status.task_id IS '交易代碼';
COMMENT ON COLUMN t_dr_status.msg_id IS '訊息ID，英數字都有，最大長度30';
COMMENT ON COLUMN t_dr_status.status IS '發送結果，DR代碼，請參考DR回傳代碼';
COMMENT ON COLUMN t_dr_status.insert_date IS '插入時間，默認為當前時間';

-- 创建 t_mo_messages 表
CREATE TABLE t_mo_messages (
    trantion_no_seq BIGSERIAL PRIMARY KEY,
    "From" VARCHAR(255) NOT NULL,
    Msg TEXT NOT NULL,
    "To" VARCHAR(255) NOT NULL,
    msg_id VARCHAR(30) NOT NULL,
    insert_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON COLUMN t_mo_messages.trantion_no_seq IS '交易編號，自動增長';
COMMENT ON COLUMN t_mo_messages."From" IS '發送號碼';
COMMENT ON COLUMN t_mo_messages.Msg IS '訊息內容，內容為UTF8編碼';
COMMENT ON COLUMN t_mo_messages."To" IS '手機用戶傳送之短碼';
COMMENT ON COLUMN t_mo_messages.msg_id IS '訊息ID，英數字都有，最大長度30';
COMMENT ON COLUMN t_mo_messages.insert_date IS '插入時間，默認為當前時間';
