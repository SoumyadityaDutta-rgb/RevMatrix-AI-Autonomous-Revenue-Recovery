"""
RevMatrix AI - Configuration Module
"""
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "RevMatrix AI"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    
    # Razorpay Credentials (defaults to Sandbox Mock mode if test keys aren't supplied)
    RAZORPAY_KEY_ID: str = os.getenv("RAZORPAY_KEY_ID", "rzp_test_revmatrix_demo")
    RAZORPAY_KEY_SECRET: str = os.getenv("RAZORPAY_KEY_SECRET", "mock_secret_key_revmatrix_2026")
    RAZORPAY_WEBHOOK_SECRET: str = os.getenv("RAZORPAY_WEBHOOK_SECRET", "webhook_secret_revmatrix")
    
    # Compliance & Guardrails Defaults
    MAX_ATTEMPTS_PER_48H: int = 3
    QUIET_HOURS_START_IST: int = 21  # 9 PM IST
    QUIET_HOURS_END_IST: int = 8     # 8 AM IST
    
    # Recovery Heuristics
    SALARY_START_DAY: int = 1
    SALARY_END_DAY: int = 7
    
    class Config:
        env_file = ".env"

settings = Settings()
