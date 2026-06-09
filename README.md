---
title: Card2vCard
emoji: 📇
colorFrom: blue
colorTo: indigo
sdk: gradio
sdk_version: "4.44.1"
app_file: app/app.py
pinned: false
---

# Card2vCard

Upload a business card. Get back a `.vcf` contact file you can import straight into your phone, or scan the QR code on the spot.

Built with GPT-4o vision, Gradio, and Airtable. Runs on Hugging Face Spaces.

---

## What it does

1. Upload a photo of any business card
2. GPT-4o extracts name, company, title, emails, phones, website, and address
3. Review and edit the extracted fields before exporting
4. Download a `.vcf` file or scan the QR code directly from the screen
5. Card is saved to your private Airtable vault for later retrieval

Images are never stored. Only the extracted contact fields are saved.


## Environment variables

| Variable | Required | Description |
|---|---|---|
| `OPENAI_API_KEY` | Yes | OpenAI key with GPT-4o access |
| `AIRTABLE_API_KEY` | Optional | Personal Access Token from airtable.com/create/tokens (scopes: records:read + records:write) |
| `AIRTABLE_BASE_ID` | Optional | Base ID from your Airtable URL (starts with `app...`) |
| `AIRTABLE_TABLE_NAME` | Optional | Table name in that base, e.g. `Cards` |
| `GRADIO_PASSWORD` | Optional | Password for the login wall (username: `remko`) |
| `OCR_BACKEND` | Optional | Set to `mock` for keyless local testing. Defaults to `openai`. |

The vault tab only appears when all three Airtable vars are set.

---

## Airtable table setup (one-time)

Create a table with these fields:

| Field name | Type |
|---|---|
| Name | Single line text |
| Company | Single line text |
| Title | Single line text |
| Emails | Long text |
| Phones | Long text |
| Website | URL |
| Address | Long text |

---

## Deploy to Hugging Face Spaces

1. Create a new Space (Gradio SDK, Python 3.11)
2. Add Space secrets: `OPENAI_API_KEY`, `AIRTABLE_API_KEY`, `AIRTABLE_BASE_ID`, `AIRTABLE_TABLE_NAME`, `GRADIO_PASSWORD`
3. Push this repo. Spaces reads the YAML header at the top of this file and starts `app/app.py`

---

## How it works

The extraction lives in `app/ocr_core.py` as a backend-agnostic function:

```python
extract(image_bytes, schema, backend="openai")
```

The schema is a Pydantic model (`schemas.py`). The OpenAI backend encodes the image as base64, sends it to GPT-4o with JSON mode, and validates the response against the schema. The formatter (`formatters.py`) produces a vCard 3.0 string, which is also encoded as a QR code.

The same `extract()` function can be pointed at any other schema: bank statement fields, warranty details, anything with a photo and structured output. The core is engine-agnostic.

---

## License

MIT, see [LICENSE](LICENSE).
