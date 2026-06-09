import os

from schemas import BusinessCardSchema


def vault_enabled() -> bool:
    return bool(os.getenv("AIRTABLE_API_KEY"))


def _table():
    from pyairtable import Api
    api = Api(os.environ["AIRTABLE_API_KEY"])
    return api.table(os.environ["AIRTABLE_BASE_ID"], os.environ["AIRTABLE_TABLE_NAME"])


def save_card(card: BusinessCardSchema) -> dict:
    data = card.model_dump()
    fields = {
        "Name": data.get("full_name") or "",
        "Company": data.get("company") or "",
        "Title": data.get("title") or "",
        "Emails": ", ".join(data.get("emails") or []),
        "Phones": ", ".join(data.get("phones") or []),
        "Website": data.get("website") or "",
        "Address": data.get("address") or "",
    }
    fields = {k: v for k, v in fields.items() if v}
    return _table().create(fields)


def list_cards() -> list[dict]:
    records = _table().all()
    records.sort(key=lambda r: r.get("createdTime", ""), reverse=True)
    result = []
    for r in records:
        f = r.get("fields", {})
        emails_str = f.get("Emails", "")
        phones_str = f.get("Phones", "")
        result.append({
            "full_name": f.get("Name", ""),
            "company": f.get("Company", ""),
            "title": f.get("Title", ""),
            "emails": [e.strip() for e in emails_str.split(",") if e.strip()],
            "phones": [p.strip() for p in phones_str.split(",") if p.strip()],
            "created_at": r.get("createdTime", ""),
        })
    return result
