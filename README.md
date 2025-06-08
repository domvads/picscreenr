# picscreenr

A simple Flask application for uploading images, generating captions and tags, and identifying people across images using face recognition and clothing feature matching.

## Prerequisites

- Python 3.8–3.11 are known to work with `dlib`; newer versions such as 3.13
  currently lack prebuilt wheels.  Using Python 3.11 or earlier is therefore
  strongly recommended.
- On Windows, make sure to use a 64‑bit Python and install Visual Studio
  Build Tools as well as CMake so that the `dlib` library required by
  `face_recognition` can compile.  An error like `python313t.lib` missing often
  indicates an unsupported Python version.
- A recent version of the `transformers` library (e.g. 4.26 or newer) is
  required for caption generation.  Older releases may raise
  `NotImplementedError` when using beam search.

Verify CMake is accessible:
```bash
cmake --version
```


## Setup

Install dependencies:
```bash
pip install -r requirements.txt
```
On Windows the `py` launcher should be used for both installation and running
the app to ensure the same Python interpreter is used:
```powershell
py -m pip install -r requirements.txt
```

Run the application:
```bash
python app.py
```
On Windows:
```powershell
py app.py
```

Use `/upload_image` endpoint with a POST request containing an image file under `file` field.

## Endpoints
- `POST /upload_image` – upload an image.
- `GET /description/<image_id>` – get caption and tags for an uploaded image.
- `GET /identify/<image_id>` – get recognized person IDs with confidence scores.

## GUI Uploader

A small Tkinter interface is provided in `gui.py` to upload all images from a selected folder to the running server.

Run the Flask app using `python app.py` and then execute:
```bash
python gui.py
```
Choose the folder containing your images and they will be uploaded automatically.

## License

This project is licensed under the terms of the [MIT License](LICENSE).
