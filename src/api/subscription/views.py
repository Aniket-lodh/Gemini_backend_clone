from typing import Any
from fastapi import APIRouter, Depends, HTTPException

from src.api.authentication import schemas as auth_schemas, services as auth_services
from src.api.subscription import schemas, services

router = APIRouter(prefix="/subscribe", tags=["Subscription"])


@router.post("/pro")
async def subscribe_pro(
    user: auth_schemas.User = Depends(auth_services.get_current_user),
) -> schemas.StripeCheckoutResponse:
    """Initiates a Pro subscription via Stripe Checkout."""
    checkout_response = await services.initiate_stripe_checkout(user.id)
    return checkout_response


@router.get("/status", response_model=schemas.SubscriptionStatus)
async def get_subscription_status(
    user: auth_schemas.User = Depends(auth_services.get_current_user),
) -> Any:
    """Checks the user's current subscription tier (Basic or Pro)."""
    status = await services.get_subscription_status(user.id)
    return status