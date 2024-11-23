import jwt
import datetime
from typing import Dict, Any

# 設定密鑰
SECRET_KEY = "your_secret_key"

# 生成 JWT Token
def generate_jwt(payload: Dict[str, Any], secret_key: str = SECRET_KEY) -> str:
    """
    根據提供的有效載荷生成 JWT token
    :param payload: JWT 載荷（例如：用戶 ID，過期時間等）
    :param secret_key: 用於簽名的密鑰
    :return: 生成的 JWT Token
    """
    # 設定發行時間 (iat) 和過期時間 (exp)
    # 發行時間
    payload["iat"] = datetime.datetime.now(datetime.timezone.utc)  
    # 過期時間，1 小時
    payload["exp"] = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)  

    # 使用 HS256 加密算法生成 JWT
    token = jwt.encode(payload, secret_key, algorithm="HS256")
    return token

# 解密 JWT Token
def decode_jwt(token: str, secret_key: str = SECRET_KEY) -> Dict[str, Any]:
    """
    解密 JWT Token 並返回載荷
    :param token: 要解密的 JWT Token
    :param secret_key: 用於驗證的密鑰
    :return: JWT 載荷內容（字典形式）
    """
    try:
        # 解碼並驗證 JWT Token
        decoded = jwt.decode(token, secret_key, algorithms=["HS256"], options={"verify_exp": True})
        return decoded
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")
