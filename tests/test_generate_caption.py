import types
import importlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def test_generate_caption_falls_back(tmp_path):
    # stub transformers
    transformers = types.ModuleType("transformers")
    transformers.VisionEncoderDecoderModel = object
    transformers.ViTImageProcessor = object
    transformers.AutoTokenizer = object
    sys.modules["transformers"] = transformers

    # stub PIL
    pil = types.ModuleType("PIL")
    class DummyImage:
        def convert(self, mode):
            return self
    pil_image = types.ModuleType("PIL.Image")
    pil_image.open = lambda *a, **k: DummyImage()
    pil.Image = pil_image
    sys.modules["PIL"] = pil
    sys.modules["PIL.Image"] = pil_image

    # stub torch
    torch_stub = types.ModuleType("torch")
    torch_stub.cuda = types.SimpleNamespace(is_available=lambda: False)
    torch_stub.device = lambda name: name
    sys.modules["torch"] = torch_stub

    # import module with stubs
    mod = importlib.import_module("services.image_caption")
    importlib.reload(mod)

    class DummyModel:
        def to(self, device):
            pass
        def generate(self, pixel_values, max_length=16, num_beams=4):
            if num_beams != 1:
                raise NotImplementedError
            return [[0]]

    class DummyProcessor:
        def __call__(self, images, return_tensors="pt"):
            class Out:
                def __init__(self):
                    self.pixel_values = self
                def to(self, device):
                    return self
            return Out()

    class DummyTokenizer:
        def decode(self, ids, skip_special_tokens=True):
            return "ok"

    caption = mod.generate_caption(DummyModel(), DummyProcessor(), DummyTokenizer(), str(tmp_path / "img.png"))
    assert caption == "ok"
