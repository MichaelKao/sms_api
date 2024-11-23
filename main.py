# main.py
from fastapi import FastAPI
from controller.sms_controller import sms_router 

app = FastAPI(
    title="SMS Service API",
    version="1.0",
    description="SMS service API",
    debug=True,
)

app.include_router(
    sms_router,
    prefix="/sms",
    tags=["SMS API"],
)