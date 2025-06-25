import importlib
import os
import sys

# Ensure the package root is importable when pytest modifies sys.path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

def test_import_sync_client():
    module = importlib.import_module('perplexity')
    client = getattr(module, 'Client', None)
    assert client is not None

def test_import_async_client():
    module = importlib.import_module('perplexity_async')
    client = getattr(module, 'Client', None)
    assert client is not None


def test_import_generators():
    img_mod = importlib.import_module('packages.generators.image_generator')
    assert hasattr(img_mod, 'generate_image')
    audio_mod = importlib.import_module('packages.generators.audio_generator')
    assert hasattr(audio_mod, 'text_to_speech')
    video_mod = importlib.import_module('packages.generators.video_generator')
    assert hasattr(video_mod, 'create_video')
