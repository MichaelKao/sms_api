# controller.py
from fastapi import APIRouter, HTTPException, Form
from pydantic import BaseModel, Field
from service.sms_service import SmsService
from typing import List, Optional

# 初始化 Service
sms_service = SmsService()

sms_router = APIRouter()

# 發送簡訊Request
class SMSRequest(BaseModel):
    acc: str = Form(..., description="平台帳號(請使用貴公司在本平台的帳號)")
    pas: str = Form(..., description="平台密碼(請使用貴公司在本平台的密碼)")
    subacc: Optional[str] = Form(None, description="子帳號(CDR分帳用)")
    from_: str = Form(..., alias="from", description="指定發訊方號碼(企業短碼或長碼)")
    msg: str = Form(..., description="訊息內容(請傳UTF8編碼, 中文限制70字, 英文160字)")
    To: List[str] = Form(..., description="收訊者門號, 可使用陣列一次發送多筆簡訊")
    expiretime: Optional[int] = Form(86400, description="簡訊發送截止時間(秒), 預設86400秒")
    retry: Optional[str] = Form('Y', description="是否開啟retry, Y啟用, N關閉 (預設為Y)")
    autosplit: Optional[str] = Form('N', description="是否啟用長簡訊, N關閉(預設)或 Y啟用")
    priority: Optional[int] = Form(0, description="發送優先順序, 0為標準, 1為較高 (預設為0)")

    class Config:
        alias_generator = lambda name: name.replace('_', '')
        
# 發送簡訊Response
class SMSResponse(BaseModel):
    task_id: str = Field(..., description="交易代碼(YYYYMMDDHHMMSS+短碼+5位隨機數字)")
    code: str = Field(..., description="回傳代碼, 請參考API回傳代碼列表")
    
# 接收即時 DR 狀態更新Request
class DRRequest(BaseModel):
    task_id: str = Field(..., description="交易代碼")
    msg_id: str = Field(..., max_length=30, description="訊息ID，英數字都有，最大長度30")
    status: str = Field(..., description="發送結果，DR代碼，請參考DR回傳代碼")
    
# 接收即時 DR 狀態更新Response
class DRResponse(BaseModel):
    code: int = Field(..., description="回傳代碼(1:成功、2:失敗)")
    
# 接收即時 MO 簡訊通知Request 
class MORequest(BaseModel):
    From: str = Field(..., description="發送號碼")
    Msg: str = Field(..., description="訊息內容，內容為UTF8編碼")
    To: str = Field(..., description="手機用戶傳送之短碼")
    msg_id: str = Field(..., max_length=30, description="訊息ID，英數字都有，最大長度30")
    
# 接收即時 MO 簡訊通知Response
class MOResponse(BaseModel):
    code: str = Field(..., description="回傳代碼 (1:成功、2:失敗)")
    
# 發送簡訊
@sms_router.post("/api/send_sms", response_model=SMSResponse, summary="發送簡訊", description=("此功能提供給企業用戶透過 HTTP Post API 傳送即時簡訊發送之需求"))
async def send_sms(data: SMSRequest):
    try:
        # 發送簡訊
        response = sms_service.send_sms(data.model_dump(by_alias=True))
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
    
# 接收即時 DR 狀態更新    
@sms_router.post("/api/receive_dr_status", response_model=DRResponse, summary="接收即時 DR 狀態更新", description=("此功能提供給企業用戶透過 HTTP Post API，即時接收DR狀態"))
async def receive_dr_status(data: DRRequest):
    try:
        # 接收即時 DR 狀態更新
        response = sms_service.receive_dr_status(data.model_dump(by_alias=True))
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

# 接收即時 MO 簡訊通知
@sms_router.post("/api/mo_notice", response_model=MOResponse, summary="接收即時 MO 簡訊通知", description=("此功能提供給企業用戶透過 HTTP Post API 接收即時MO簡訊通知"))
async def mo_notice(data: MORequest):
    try:
        # 接收即時 MO 簡訊通知
        response = sms_service.mo_notice(data.model_dump(by_alias=True))
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


