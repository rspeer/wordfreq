from __future__ import annotations

from pathlib import Path

import locate


def data_path(filename: str | None = None) -> Path:
    """
    Get a path to a file in the data directory.
    """
    if filename is None:
        return Path(locate.this_dir(), "data")
    else:
        return Path(locate.this_dir(), "data", filename)
