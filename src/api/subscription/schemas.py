from pydantic import BaseModel


class StripeCheckoutResponse(BaseModel):
    session_id: str
    checkout_url: str


class SubscriptionStatus(BaseModel):
    active: bool
    plan: str
