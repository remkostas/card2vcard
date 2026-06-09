import os
import sys

import vobject

# Make the app package importable when running pytest from the repo root.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app"))

from formatters import to_qr_image, to_vcard  # noqa: E402
from ocr_core import extract  # noqa: E402
from schemas import BusinessCardSchema  # noqa: E402


def _sample_card():
    return BusinessCardSchema(
        full_name="Jordan Avery",
        company="Northwind Labs",
        title="Head of Partnerships",
        emails=["jordan.avery@northwind.example", "j.avery@northwind.example"],
        phones=["+49 30 1234567"],
        website="https://northwind.example",
        address="Friedrichstrasse 12, 10117 Berlin",
    )


def test_vcard_has_required_envelope():
    out = to_vcard(_sample_card())
    assert out.startswith("BEGIN:VCARD")
    assert out.strip().endswith("END:VCARD")
    assert "VERSION:3.0" in out


def test_vcard_parses_with_real_parser():
    """The generated .vcf must round-trip through a real vCard parser."""
    out = to_vcard(_sample_card())
    card = vobject.readOne(out)
    assert card.fn.value == "Jordan Avery"
    assert card.org.value[0] == "Northwind Labs"
    emails = {e.value for e in card.contents.get("email", [])}
    assert "jordan.avery@northwind.example" in emails
    assert len(card.contents.get("email", [])) == 2  # both emails kept
    assert len(card.contents.get("tel", [])) == 1


def test_vcard_n_field_splits_name():
    out = to_vcard(_sample_card())
    card = vobject.readOne(out)
    # N is structured as Family;Given;...
    assert card.n.value.family == "Avery"
    assert card.n.value.given == "Jordan"


def test_vcard_skips_empty_fields():
    out = to_vcard(BusinessCardSchema(full_name="Solo Name"))
    assert "ORG:" not in out
    assert "TITLE:" not in out
    assert "EMAIL" not in out


def test_qr_image_is_generated():
    out = to_vcard(_sample_card())
    img = to_qr_image(out)
    assert img.size[0] > 0 and img.size[1] > 0


def test_mock_backend_runs_keyless():
    card = extract(b"not-a-real-image", BusinessCardSchema, backend="mock")
    assert isinstance(card, BusinessCardSchema)
    assert card.full_name
    # full mock pipeline must produce a parseable vCard
    parsed = vobject.readOne(to_vcard(card))
    assert parsed.fn.value == card.full_name


def test_unknown_backend_raises():
    try:
        extract(b"x", BusinessCardSchema, backend="nope")
    except ValueError:
        return
    raise AssertionError("expected ValueError for unknown backend")
