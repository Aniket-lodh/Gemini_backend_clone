from fastapi import APIRouter, Depends, Request
from sqlmodel import Session

from src.api.subscription import schemas, services
from src.core.db_pool import DataBasePool
from src.decorators.auth_required import authentication_required
from src.decorators.catch_async import catch_async
from src.utils.format_response import format_response

router = APIRouter(prefix="/subscribe", tags=["Subscription"])


@router.post("/pro", description="Initiates a Pro subscription via Stripe Checkout.")
@catch_async
@authentication_required
async def subscribe_pro(
    request: Request,
    db_pool: Session = Depends(DataBasePool.get_pool),
) -> schemas.StripeCheckoutResponse:
    return await services.initiate_stripe_checkout(request.state.user.uid, db_pool)

# TODO: Implement this, Implement what to do in checkout page.
# @router.get(
#     "/status",
#     description="Checks the user's current subscription tier (Basic or Pro).",
#     response_model=schemas.SubscriptionStatus,
# )
# @catch_async
# @authentication_required
# async def get_subscription_status(request: Request):
#     return await services.get_subscription_status(request.state.user.uid)


@router.get(
    "/success",
    description="Stripe Payment success redirect page.",
)
@catch_async
async def stripe_success_payment():
    return format_response(message="Payment successful.")


@router.get(
    "/cancel",
    description="Stripe Payment canceled redirect page.",
)
@catch_async
async def stripe_canceled_payment():
    return format_response(message="Payment Canceled.")
