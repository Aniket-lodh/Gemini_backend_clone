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
    except Exception:
        return None  # Signature or webhook secret is invalid

    event_type = event["type"]
    data = event["data"]["object"]

    print("event_type", event_type)
    session_id = data.get("id")
    if event_type == "checkout.session.completed":
        customer_id = data.get("customer")
        return await handle_checkout_completed(customer_id, session_id, db_pool)
    elif event_type == "checkout.session.expired":
        return await handle_checkout_expired(session_id, db_pool)

    return True  # Unhandled event, but valid signature, so we simply return 200


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
        # Deactive user old plan.
        existing_plan = await db.get_attr(
            dbClassName=TableNameEnum.UserPlan,
            uid=user.uid,
            where={"active": True},
            db_pool=db_pool,
        )
        if existing_plan:
            updated_plan, ok = await db.update(
                dbClassName=TableNameEnum.UserPlan,
                data={
                    **existing_plan.model_dump(),
                    "active": False,
                },
                db_pool=db_pool,
            )
            print("updated_plan", updated_plan)
        new_plan, ok = await db.insert(
            dbClassName=TableNameEnum.UserPlan,
            data={
                "user_id": user.uid,
                "active": True,
                "plan": "pro",
            },
            db_pool=db_pool,
        )
        if ok is False:
            raise HTTPException(
                detail="Failed to create new plan",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        _, ok = await db.update(
            dbClassName=TableNameEnum.Transactions,
            data={
                **existing_transaction.model_dump(),
                "status": "completed",
                "plan_id": new_plan.plan_id,
            },
            db_pool=db_pool,
        )
        if ok is False:
            raise HTTPException(
                detail="Failed to update transaction",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    db_pool.commit()
    return True


async def handle_checkout_expired(session_id: str, db_pool: Session):
    existing_transaction = await db.get_attr(
        dbClassName=TableNameEnum.Transactions,
        transaction_id=session_id,
        db_pool=db_pool,
    )
    if existing_transaction is None:
        raise HTTPException(
            detail="Transaction not found.",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    _, ok = await db.update(
        dbClassName=TableNameEnum.Transactions,
        data={
            **existing_transaction.model_dump(),
            "status": "expired",
        },
        db_pool=db_pool,
    )
    if not ok:
        raise HTTPException(
            detail="Failed to update expired transaction",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    db_pool.commit()
    return True
