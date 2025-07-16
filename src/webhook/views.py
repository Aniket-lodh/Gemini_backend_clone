import traceback
from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlmodel import Session
from src.core.db_pool import DataBasePool

from src.webhook import services

router = APIRouter(prefix="/webhook", tags=["Webhooks"])


@router.post("/stripe")
async def stripe_webhook(
    request: Request,
    db_pool: Session = Depends(DataBasePool.get_pool),
) -> dict[str, str]:
    """Handles Stripe webhook events (e.g., payment success/failure)."""
    payload = await request.body()
    stripe_signature = request.headers.get("stripe-signature")
    try:
        event = await services.process_stripe_webhook(
            payload, stripe_signature, db_pool
        )
        if event:
            return {"status": "success", "message": "Stripe webhook processed."}
        else:
            raise HTTPException(status_code=400, detail="Invalid signature")

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))
