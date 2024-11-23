from sqlalchemy import Column, Integer, String, Text, JSON, TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

# 建立基底類
Base = declarative_base()

class SmsRequest(Base):
    __tablename__ = "t_sms_requests"

    trantion_no_seq = Column("trantion_no_seq", Integer, primary_key=True, autoincrement=True)
    acc = Column(String(255), nullable=False)
    pas = Column(String(255), nullable=False)
    subacc = Column(String(255), default=None)
    from_ = Column("from", String(255), nullable=False)
    msg = Column(Text, nullable=False)
    to_ = Column("to", JSON, nullable=False)
    expire_time = Column("expire_time", Integer, default=86400)
    retry = Column(String(1), default="Y")
    auto_split = Column("auto_split", String(1), default="N")
    priority = Column(Integer, default=0)
    insert_date = Column("insert_date", TIMESTAMP, default=func.now())
