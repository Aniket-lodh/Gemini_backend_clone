import platform
from src.celery.config import celery_app
from src.celery.service import *

if __name__ == "__main__":
    system = platform.system()
    
    pool = "prefork" if system != "Windows" else "solo"

    celery_app.worker_main([
        "worker",
        "--loglevel=INFO",
        "--pool", pool,
        "-Q", "default,send_gemini_message",
    ])
