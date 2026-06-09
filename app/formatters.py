import io

import qrcode
import qrcode.constants
from PIL import Image

from schemas import BusinessCardSchema


def to_vcard(card: BusinessCardSchema) -> str:
    lines = ["BEGIN:VCARD", "VERSION:3.0"]

    if card.full_name:
        lines.append(f"FN:{card.full_name}")
        parts = card.full_name.rsplit(" ", 1)
        if len(parts) == 2:
            lines.append(f"N:{parts[1]};{parts[0]};;;")
        else:
            lines.append(f"N:{card.full_name};;;;")

    if card.company:
        lines.append(f"ORG:{card.company}")

    if card.title:
        lines.append(f"TITLE:{card.title}")

    for email in card.emails:
        if email.strip():
            lines.append(f"EMAIL;TYPE=INTERNET:{email.strip()}")

    for phone in card.phones:
        if phone.strip():
            lines.append(f"TEL;TYPE=WORK,VOICE:{phone.strip()}")

    if card.website:
        lines.append(f"URL:{card.website}")

    if card.address:
        lines.append(f"ADR;TYPE=WORK:;;{card.address};;;;")

    lines.append("END:VCARD")
    return "\r\n".join(lines)


def to_qr_image(vcard_str: str) -> Image.Image:
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(vcard_str)
    qr.make(fit=True)

    img_obj = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img_obj.save(buf, format="PNG")
    buf.seek(0)
    return Image.open(buf).copy()
