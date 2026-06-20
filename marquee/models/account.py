from pydantic import BaseModel


class BankAccount(BaseModel):
    id: str
    bank_name: str
    account_name: str
    account_type: str = "custody"  # custody, savings, trading
    currency: str = "CHF"
