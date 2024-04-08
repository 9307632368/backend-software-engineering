"""Load a lesson's independent app.py without requiring package renaming."""
import importlib.util
from pathlib import Path
import sys
from functools import lru_cache

import pytest

TUTORIALS = Path(__file__).resolve().parents[1] / "01-fundamentals" / "tutorials"


@lru_cache(maxsize=None)
def _load(slug: str):
    module_path = TUTORIALS / slug / "app.py"
    if not module_path.exists():
        raise FileNotFoundError(module_path)
    module_name = "lesson_" + slug.replace("-", "_")
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def load_tutorial():
    return _load


EXAMPLES = Path(__file__).resolve().parents[1] / "01-fundamentals" / "examples"

@lru_cache(maxsize=None)
def _load_example(slug: str):
    module_path = EXAMPLES / slug / "app.py"
    module_name = "example_" + slug.replace("-", "_")
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

@pytest.fixture
def load_example():
    return _load_example
