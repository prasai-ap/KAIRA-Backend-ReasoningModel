from pydantic import BaseModel


class EsewaInitiateResponse(BaseModel):
    payment_url: str
    form_data: dict


class SubscriptionResponse(BaseModel):
    is_active: bool
    plan_name: str | None = None
    end_date: str | None = None