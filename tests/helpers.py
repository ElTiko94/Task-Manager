from importlib import util
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]

def load_module(name: str):
    """Load a module from the project root without modifying sys.path."""
    if name in sys.modules:
        return sys.modules[name]
    module_path = ROOT / f"{name}.py"
    spec = util.spec_from_file_location(name, module_path)
    module = util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module
