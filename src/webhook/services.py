from fastapi import HTTPException, status
from sqlmodel import Session
import stripe
from src.core.variables import STRIPE_WEBHOOK_SECRET
from src.core.db_methods import DB
from src.core.db_models import TableNameEnum
from src.core.variables import STRIPE_WEBHOOK_SECRET

db = DB()


async def process_stripe_webhook(
    payload: bytes, stripe_signature: str, db_pool: Session
):
    try:
        decoded_payload = payload.decode()
        event = stripe.Webhook.construct_event(
            payload=decoded_payload,
            sig_header=stripe_signature,
            secret=STRIPE_WEBHOOK_SECRET,
        )
    except Exception as e:
        return None  # Signature or webhook secret isinvalid

    event_type = event["type"]
    data = event["data"]["object"]

    print("event_type", event_type)
    if event_type == "checkout.session.completed":
        customer_id = data.get("customer")
        session_id = data.get("id")
        return await handle_checkout_completed(customer_id, session_id, db_pool)

    # elif event_type == "customer.subscription.deleted":
    #     customer_id = data.get("customer")
    #     return handle_subscription_deleted(customer_id)

    # Add more handlers if needed
    return True  # Unhandled event, but valid signature


async def handle_checkout_completed(
    customer_id: str, session_id: str, db_pool: Session
):
    user = await db.get_attr(
        dbClassName=TableNameEnum.Users, customer_id=customer_id, db_pool=db_pool
    )
    if user:
        # Before updating the transaction details we are doing one final retrieve.
        existing_transaction = await db.get_attr(
            dbClassName=TableNameEnum.Transactions,
            transaction_id=session_id,
            db_pool=db_pool,
        )
        if existing_transaction is None:
            raise HTTPException(
                detail="Transaction not found", status_code=status.HTTP_404_NOT_FOUND
            )
        updated_user, ok = await db.update(
            dbClassName=TableNameEnum.Transactions,
            data={
                **existing_transaction.model_dump(),
                "status": "completed",
            },
            db_pool=db_pool,
        )
        if ok is False:
            raise HTTPException(
                detail="Failed to update transaction",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        new_plan, ok = await db.insert(
            dbClassName=TableNameEnum.UserPlan,
            data={
                "user_id": user.uid,
                "active": True,
                "stripe_subscription_status": "active",
            },
            db_pool=db_pool,
        )
        if ok is False:
            raise HTTPException(
                detail="Failed to create new plan",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
    db_pool.commit()
    return True
