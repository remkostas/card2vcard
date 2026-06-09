import os
import tempfile

from dotenv import load_dotenv

load_dotenv()

import gradio as gr

from db import list_cards, save_card, vault_enabled
from formatters import to_qr_image, to_vcard
from ocr_core import extract
from schemas import BusinessCardSchema

_VAULT_ON = vault_enabled()
_BACKEND = os.getenv("OCR_BACKEND", "openai")

_PRIVACY_NOTICE = (
    "*Images are not stored. Extracted contact info is saved to your private vault.*"
    if _VAULT_ON
    else "*Images are not stored. Processing happens in real time and nothing is saved.*"
)


def run_extraction(image_path):
    if image_path is None:
        return (gr.update(visible=False),) + ("",) * 7

    with open(image_path, "rb") as f:
        image_bytes = f.read()

    card = extract(image_bytes, BusinessCardSchema, backend=_BACKEND)

    return (
        gr.update(visible=True),
        card.full_name or "",
        card.company or "",
        card.title or "",
        ", ".join(card.emails),
        ", ".join(card.phones),
        card.website or "",
        card.address or "",
    )


def generate_output(full_name, company, title, emails_str, phones_str, website, address):
    card = BusinessCardSchema(
        full_name=full_name or None,
        company=company or None,
        title=title or None,
        emails=[e.strip() for e in emails_str.split(",") if e.strip()],
        phones=[p.strip() for p in phones_str.split(",") if p.strip()],
        website=website or None,
        address=address or None,
    )

    vcard_str = to_vcard(card)
    qr_img = to_qr_image(vcard_str)

    if _VAULT_ON:
        save_card(card)

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".vcf", mode="w", encoding="utf-8")
    tmp.write(vcard_str)
    tmp.close()

    return tmp.name, qr_img, gr.update(visible=True)


def refresh_vault():
    rows = list_cards()
    return [
        [
            r.get("full_name") or "",
            r.get("company") or "",
            r.get("title") or "",
            ", ".join(r.get("emails") or []),
            ", ".join(r.get("phones") or []),
            (r.get("created_at") or "")[:10],
        ]
        for r in rows
    ]


def _show_loading():
    return (
        gr.update(value="Reading the card. This usually takes a few seconds.", visible=True),
        gr.update(interactive=False),
    )


def _clear_loading():
    return gr.update(value="", visible=False), gr.update(interactive=True)


with gr.Blocks(title="Card2vCard", theme=gr.themes.Soft()) as demo:
    with gr.Tab("Scan a card"):
        gr.Markdown("# Card2vCard")
        gr.Markdown(
            "Upload a business card. Get a contact you can import, or a QR code to scan straight to your phone."
        )
        gr.Markdown(_PRIVACY_NOTICE)

        with gr.Row():
            with gr.Column(scale=1):
                image_input = gr.Image(type="filepath", label="Business card photo", sources=["upload"])
                extract_btn = gr.Button("Extract contact", variant="primary")
                status_md = gr.Markdown("", visible=False)

            with gr.Column(scale=1, visible=False) as fields_col:
                gr.Markdown("### Review and edit")
                full_name = gr.Textbox(label="Name")
                company = gr.Textbox(label="Company")
                title = gr.Textbox(label="Title")
                emails = gr.Textbox(label="Email(s)", placeholder="Separate multiple with commas")
                phones = gr.Textbox(label="Phone(s)", placeholder="Separate multiple with commas")
                website = gr.Textbox(label="Website")
                address = gr.Textbox(label="Address")
                generate_btn = gr.Button("Generate .vcf + QR", variant="secondary")

        with gr.Row(visible=False) as output_row:
            vcf_file = gr.File(label="Download .vcf")
            qr_image = gr.Image(label="QR code, scan to save contact", type="pil")

        extract_btn.click(
            _show_loading,
            outputs=[status_md, extract_btn],
        ).then(
            run_extraction,
            inputs=[image_input],
            outputs=[fields_col, full_name, company, title, emails, phones, website, address],
        ).then(
            _clear_loading,
            outputs=[status_md, extract_btn],
        )

        generate_btn.click(
            generate_output,
            inputs=[full_name, company, title, emails, phones, website, address],
            outputs=[vcf_file, qr_image, output_row],
        )

    if _VAULT_ON:
        with gr.Tab("My Vault"):
            gr.Markdown("### Saved contacts")
            vault_table = gr.Dataframe(
                headers=["Name", "Company", "Title", "Emails", "Phones", "Date"],
                datatype=["str"] * 6,
                interactive=False,
            )
            refresh_btn = gr.Button("Refresh vault")
            refresh_btn.click(refresh_vault, inputs=[], outputs=[vault_table])


if __name__ == "__main__":
    pwd = os.getenv("GRADIO_PASSWORD")
    auth = [("remko", pwd)] if pwd else None
    demo.queue()
    demo.launch(auth=auth)
