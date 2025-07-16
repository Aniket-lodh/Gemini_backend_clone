from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlmodel import Session
from src.core.db_pool import DataBasePool
from src.decorators.catch_async import catch_async
from src.utils.format_response import format_response

from src.webhook import services

router = APIRouter(prefix="/webhook", tags=["Webhooks"])


@router.post(
    "/stripe",
    description="Handles Stripe webhook events (e.g., payment success/failure).",
)
@catch_async
async def stripe_webhook(
    request: Request,
    db_pool: Session = Depends(DataBasePool.get_pool),
) -> dict[str, str]:
    payload = await request.body()
    stripe_signature = request.headers.get("stripe-signature", "")
    event = await services.process_stripe_webhook(payload, stripe_signature, db_pool)
    if event:
        return format_response(message="Stripe webhook processed.")
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid signature"
        )
