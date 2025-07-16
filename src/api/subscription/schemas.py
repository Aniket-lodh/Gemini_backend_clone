from pydantic import BaseModel


class StripeCheckoutResponse(BaseModel):
    session_id: str


class SubscriptionStatus(BaseModel):
    active: bool
    plan: str
