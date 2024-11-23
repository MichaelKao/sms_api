import socket
import ssl

def create_ssl_server(certfile, keyfile, host='localhost', port=4443):
    """
    創建一個 SSL 伺服器，並等待客戶端連接
    :param certfile: 伺服器證書路徑
    :param keyfile: 伺服器私鑰路徑
    :param host: 伺服器主機
    :param port: 伺服器端口
    """
    # 創建 SSL 上下文
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile=certfile, keyfile=keyfile)

    # 創建普通的 TCP socket 並綁定
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((host, port))
        sock.listen(5)

        while True:
            # 等待並接受客戶端連接
            client_socket, client_address = sock.accept()
            with client_socket:
                # 包裝成 SSL 加密的 socket
                ssl_socket = context.wrap_socket(client_socket, server_side=True)
                ssl_socket.close()

def create_ssl_client(host='localhost', port=4443, cafile=None):
    """
    創建一個 SSL 客戶端，並連接到指定伺服器
    :param host: 伺服器主機
    :param port: 伺服器端口
    :param cafile: 用於驗證伺服器證書的 CA 憑證（如果有自簽名證書）
    """
    # 創建 SSL 上下文
    context = ssl.create_default_context(cafile=cafile)

    # 創建並包裝成 SSL 客戶端
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        ssl_socket = context.wrap_socket(sock, server_hostname=host)
        ssl_socket.connect((host, port))

        # 接收伺服器發送的數據
        data = ssl_socket.recv(1024)
        print(f"Received from server: {data.decode()}")