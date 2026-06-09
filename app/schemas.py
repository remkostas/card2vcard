from pydantic import BaseModel


class BusinessCardSchema(BaseModel):
    full_name: str | None = None
    company: str | None = None
    title: str | None = None
    emails: list[str] = []
    phones: list[str] = []
    website: str | None = None
    address: str | None = None
