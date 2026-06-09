import base64
import json
import os
from typing import TypeVar, Type

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


def extract(image_bytes: bytes, schema: Type[T], backend: str = "openai") -> T:
    if backend == "openai":
        return _extract_openai(image_bytes, schema)
    if backend == "mock":
        return _extract_mock(image_bytes, schema)
    raise ValueError(f"Unknown backend: {backend!r}")


def _extract_mock(image_bytes: bytes, schema: Type[T]) -> T:
    """Keyless backend for local dev, tests, and CI.

    Returns a fixed sample contact so the full pipeline can run without an
    API key. Activate with OCR_BACKEND=mock.
    """
    sample = {
        "full_name": "Jordan Avery",
        "company": "Northwind Labs",
        "title": "Head of Partnerships",
        "emails": ["jordan.avery@northwind.example"],
        "phones": ["+49 30 1234567"],
        "website": "https://northwind.example",
        "address": "Friedrichstrasse 12, 10117 Berlin",
    }
    valid = set(schema.model_fields)
    return schema.model_validate({k: v for k, v in sample.items() if k in valid})


def _extract_openai(image_bytes: bytes, schema: Type[T]) -> T:
    from openai import OpenAI

    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    b64 = base64.b64encode(image_bytes).decode()
    schema_json = json.dumps(schema.model_json_schema())

    response = client.chat.completions.create(
        model="gpt-4o",
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a business card reader. Extract all contact information from the image "
                    "and return a JSON object that strictly matches this schema:\n"
                    f"{schema_json}\n"
                    "Use null for missing optional fields. Use empty arrays for missing list fields. "
                    "Preserve original formatting for phone numbers."
                ),
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{b64}"},
                    }
                ],
            },
        ],
    )

    data = json.loads(response.choices[0].message.content)
    return schema.model_validate(data)
