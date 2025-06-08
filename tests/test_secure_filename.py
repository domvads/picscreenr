import io
import importlib
import sys
import types
from pathlib import Path


def create_app(tmp_path):
    # stub heavy services
    mod_caption = types.ModuleType("services.image_caption")
    mod_caption.load_model = lambda: (None, None, None)
    mod_caption.generate_caption = lambda *a, **k: ""
    mod_caption.extract_tags = lambda *a, **k: []

    mod_face = types.ModuleType("services.face_recognition")
    mod_face.detect_faces = lambda *a, **k: []
    mod_face.compare_faces = lambda *a, **k: (-1, 1.0)

    mod_feat = types.ModuleType("services.feature_matching")
    mod_feat.extract_color_histogram = lambda *a, **k: [0] * 10
    mod_feat.compare_histograms = lambda *a, **k: (-1, -1.0)

    sys.modules["services.image_caption"] = mod_caption
    sys.modules["services.face_recognition"] = mod_face
    sys.modules["services.feature_matching"] = mod_feat

    # stub PIL
    pil = types.ModuleType("PIL")

    class DummyImage:
        def convert(self, mode):
            return self

        def resize(self, size):
            return self

        def save(self, path):
            with open(path, "wb") as f:
                f.write(b"img")

    pil_image = types.ModuleType("PIL.Image")
    pil_image.open = lambda *a, **k: DummyImage()
    pil.Image = pil_image
    sys.modules["PIL"] = pil
    sys.modules["PIL.Image"] = pil_image

    app_module = importlib.import_module("app")
    importlib.reload(app_module)
    app_module.app.config["UPLOAD_FOLDER"] = str(tmp_path)
    return app_module.app


def test_filename_sanitized(tmp_path):
    app = create_app(tmp_path)
    client = app.test_client()
    data = {"file": (io.BytesIO(b"x"), "../evil.jpg")}
    rv = client.post("/upload_image", data=data, content_type="multipart/form-data")
    assert rv.status_code == 200
    assert (Path(tmp_path) / "evil.jpg").exists()
