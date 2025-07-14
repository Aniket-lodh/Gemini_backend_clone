from fastapi import APIRouter, Header, HTTPException, Request

from src.webhook import services

router = APIRouter(prefix="/webhook", tags=["Webhooks"])


@router.post("/stripe")
async def stripe_webhook(
    request: Request, stripe_signature: str = Header(None)
) -> dict[str, str]:
    """Handles Stripe webhook events (e.g., payment success/failure)."""
    payload = await request.body()
    try:
        event = services.process_stripe_webhook(payload, stripe_signature)
        if event:
            return {"status": "success", "message": "Stripe webhook processed."}
        else:
            raise HTTPException(status_code=400, detail="Invalid signature")

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
