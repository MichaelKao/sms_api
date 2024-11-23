import pika
import json
import logging

# 設置基本日誌
logging.basicConfig(level=logging.INFO)


class RabbitMQUtils:
    def __init__(self):
        # 設定連接參數，包括用戶名和密碼
        credentials = pika.PlainCredentials('TLGRDCB2BSIT', 'tlgrdcb2bAp')
        connection_params = pika.ConnectionParameters(host='localhost', credentials=credentials)

        # 連接到 RabbitMQ
        self.connection = pika.BlockingConnection(connection_params)
        self.channel = self.connection.channel()

        # 設定隊列名稱
        self.queue_name = 'sms_request_queue'

        # 確保隊列存在
        self.channel.queue_declare(queue='sms_request_queue', durable=True)

    def send_message(self, message, routing_key=None):
        """
        發送消息到指定的隊列
        :param message: 要發送的消息
        :param routing_key: 設定路由鍵，如果為 None 則使用類別初始化時的默認隊列
        """
        if routing_key is None:
            routing_key = self.queue_name

        # 將消息轉換為 JSON 格式
        message_json = json.dumps(message)

        try:
            # 發送消息
            self.channel.basic_publish(
                exchange='',
                routing_key=routing_key,
                body=message_json,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # 設置消息為持久化
                )
            )
            logging.info(f"Sent message: {message_json}")
        except Exception as e:
            logging.error(f"Failed to send message: {e}")

    def consume_messages(self, callback, auto_ack=False):
        """
        設置消費者，並處理隊列中的消息
        :param callback: 消費消息的回調函數
        :param auto_ack: 是否自動確認消息，建議設為 False
        """
        try:
            self.channel.basic_consume(
                queue=self.queue_name,
                on_message_callback=callback,
                auto_ack=auto_ack
            )
            logging.info(f"Waiting for messages in {self.queue_name}. To exit press CTRL+C")
            self.channel.start_consuming()
        except Exception as e:
            logging.error(f"Failed to consume messages: {e}")

    def ack_message(self, delivery_tag):
        """
        手動確認已處理的消息
        :param delivery_tag: 消息的標籤，用來確認消息
        """
        try:
            self.channel.basic_ack(delivery_tag=delivery_tag)
            logging.info(f"Message acknowledged with tag: {delivery_tag}")
        except Exception as e:
            logging.error(f"Failed to acknowledge message: {e}")

    def close(self):
        """關閉連接"""
        try:
            self.connection.close()
            logging.info("Connection closed.")
        except Exception as e:
            logging.error(f"Failed to close connection: {e}")
