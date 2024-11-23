# 使用 Python 官方的輕量級基礎鏡像
FROM python:3.9-slim

# 設定工作目錄
WORKDIR /app

# 複製 requirements.txt 並安裝依賴
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# 複製所有專案文件到容器中
COPY . /app/

# 開放 8000 端口（FastAPI 預設端口）
EXPOSE 8000

# 設置環境變數
ENV DATABASE_URL=postgresql://tlgrdcb2bAp:27938888@db:5432/TLGRDCB2BSIT

# 啟動 FastAPI 應用
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
