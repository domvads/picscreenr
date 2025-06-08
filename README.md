# picscreenr

A simple Flask application for uploading images, generating captions and tags, and identifying people across images using face recognition and clothing feature matching.

## Setup

Install dependencies:
```bash
pip install -r requirements.txt
```

Run the application:
```bash
python app.py
```

Use `/upload_image` endpoint with a POST request containing an image file under `file` field.

## Endpoints
- `POST /upload_image` – upload an image.
- `GET /description/<image_id>` – get caption and tags for an uploaded image.
- `GET /identify/<image_id>` – get recognized person IDs with confidence scores.
