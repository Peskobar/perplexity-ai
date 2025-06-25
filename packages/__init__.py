from pathlib import Path
import pkgutil

__all__ = []

_pkg_dir = Path(__file__).parent
for sub in _pkg_dir.iterdir():
    src = sub / "src"
    if src.is_dir():
        __path__.append(str(src))
