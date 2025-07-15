import asyncio
from src.api.chatroom import services
from src.core.db_pool import DataBasePool
from src.celery.config import celery_app
from src.utils.gemini import call_gemini_api

db = DataBasePool()
db.sync_setup()
db_pool = db.get_pool()


@celery_app.task(name="send_gemini_message")
def send_gemini_message(message_id: str, message_text: str):
    gemini_response = call_gemini_api(message_text)
    asyncio.run(services.process_gemini_response(message_id, gemini_response, db_pool))


def enqueue_gemini_call(message_id: str, message_text: str):
    send_gemini_message.delay(message_id, message_text)
