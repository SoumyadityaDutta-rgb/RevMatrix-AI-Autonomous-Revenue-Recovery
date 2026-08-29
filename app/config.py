"""
RevMatrix AI - Configuration Module
Safe configuration parser resilient to empty serverless environment variables.
"""
import os

class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "RevMatrix AI")
    APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "production" if os.getenv("VERCEL") else "development")
    
    # Razorpay Credentials (defaults to Sandbox Mock mode if test keys aren't supplied)
    RAZORPAY_KEY_ID: str = os.getenv("RAZORPAY_KEY_ID") or "rzp_test_revmatrix_demo"
    RAZORPAY_KEY_SECRET: str = os.getenv("RAZORPAY_KEY_SECRET") or "mock_secret_key_revmatrix_2026"
    RAZORPAY_WEBHOOK_SECRET: str = os.getenv("RAZORPAY_WEBHOOK_SECRET") or "webhook_secret_revmatrix"
    
    # Compliance & Guardrails Defaults
    MAX_ATTEMPTS_PER_48H: int = int(os.getenv("MAX_ATTEMPTS_PER_48H") or 3)
    QUIET_HOURS_START_IST: int = int(os.getenv("QUIET_HOURS_START_IST") or 21)  # 9 PM IST
    QUIET_HOURS_END_IST: int = int(os.getenv("QUIET_HOURS_END_IST") or 8)       # 8 AM IST
    
    # Recovery Heuristics
    SALARY_START_DAY: int = int(os.getenv("SALARY_START_DAY") or 1)
    SALARY_END_DAY: int = int(os.getenv("SALARY_END_DAY") or 7)

settings = Settings()
