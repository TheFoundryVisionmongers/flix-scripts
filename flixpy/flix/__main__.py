"""The entry point for the ``flix`` command-line utility."""

from __future__ import annotations

import sys

from .cli import main

if __name__ == "__main__":
    sys.exit(main.main())
