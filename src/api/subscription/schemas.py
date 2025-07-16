from pydantic import BaseModel


class StripeCheckoutResponse(BaseModel):
    session_id: str


class SubscriptionStatus(BaseModel):
    status: str  # "basic" or "pro"
 