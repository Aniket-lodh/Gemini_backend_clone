import stripe
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from src.core.db_models import TableNameEnum

from src.core.db_methods import DB
from src.api.subscription import schemas
from src.core.variables import (
    STRIPE_SECRET_KEY,
    STRIPE_PRO_PRICE_ID,
    STRIPE_SUCCESS_URL,
    STRIPE_CANCEL_URL,
)
from src.utils.format_response import format_response


stripe.api_key = STRIPE_SECRET_KEY
db = DB()


async def initiate_stripe_checkout(user_id: int, db_pool: Session):
    """Initiates a Stripe Checkout session for Pro subscription."""
    try:
        user = await db.get_attr(
            dbClassName=TableNameEnum.Users, uid=user_id, db_pool=db_pool
        )
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        # Creating a stripe customer if one doesn't exist
        if not user.stripe_customer_id:
            customer = stripe.Customer.create(email=user.email)
            _, ok = await db.update(
                dbClassName=TableNameEnum.Users,
                data={
                    **user.model_dump(),
                    "stripe_customer_id": customer.id,
                },
                db_pool=db_pool,
            )
            if ok is False:
                raise HTTPException(
                    detail="Failed to update user",
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
            user.stripe_customer_id = customer.id
        else:
            customer = stripe.Customer.retrieve(user.stripe_customer_id)

        checkout_session = stripe.checkout.Session.create(
            customer=customer.id,
            payment_method_types=["card"],
            line_items=[
                {
                    "price": STRIPE_PRO_PRICE_ID,
                    "quantity": 1,
                }
            ],
            mode="subscription",
            success_url=STRIPE_SUCCESS_URL,
            cancel_url=STRIPE_CANCEL_URL,
        )

        _, ok = await db.insert(
            dbClassName=TableNameEnum.Transactions,
            data={
                "transaction_id": checkout_session.id,
                "user_id": user.uid,
                "status": "pending",
                "amount": int(
                    stripe.Price.retrieve(STRIPE_PRO_PRICE_ID).unit_amount / 100
                ),
                "mode": "subscription",
            },
            db_pool=db_pool,
        )
        if not ok:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create transaction record.",
            )
        db_pool.commit()
        return format_response(
            message="Checkout session created",
            data=schemas.StripeCheckoutResponse(session_id=checkout_session.id),
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to subscribe to pro plan, please try again later.",
        )


async def get_subscription_status(user_id: str, db_pool: Session):
    """Retrieves the user's subscription status."""
    user_plan = await db.get_attr(
        dbClassName=TableNameEnum.UserPlan, uid=user_id, db_pool=db_pool
    )
    if user_plan is None:
        raise HTTPException(
            detail="User plan not found", status_code=status.HTTP_404_NOT_FOUND
        )

    return format_response(
        message="Subscription status retrieved",
        data=schemas.SubscriptionStatus(**user_plan.model_dump()).model_dump(),
    )
