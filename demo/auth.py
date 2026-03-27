"""
HTTP Basic Authentication for FastAPI
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets

security = HTTPBasic()

# 用户名和密码配置
# 在实际使用中，建议从环境变量读取
VALID_USERS = {
    "admin": "admin123",  # 请修改为强密码
    "user": "user123"     # 普通用户
}

def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    """验证用户名和密码"""
    correct_username = secrets.compare_digest(credentials.username, "admin")
    correct_password = secrets.compare_digest(credentials.password, "admin123")
    
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    return credentials.username

def verify_credentials_optional(credentials: HTTPBasicCredentials = Depends(security)):
    """可选认证 - 如果提供凭证则验证"""
    try:
        if credentials.username in VALID_USERS:
            correct_password = secrets.compare_digest(
                credentials.password, 
                VALID_USERS.get(credentials.username, "")
            )
            if correct_password:
                return credentials.username
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Basic"},
        )
    except HTTPException:
        return None
