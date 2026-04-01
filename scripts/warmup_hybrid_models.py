#!/usr/bin/env python3
from __future__ import annotations

import sys


def main() -> int:
    try:
        import easyocr
    except Exception as exc:
        print(f"EasyOCR is unavailable: {exc}", file=sys.stderr)
        return 1

    try:
        # Hybrid mode currently relies on EasyOCR. Creating a reader triggers
        # the first-run model download so extraction does not fail later.
        easyocr.Reader(["en"], gpu=False, verbose=False)
    except TypeError:
        easyocr.Reader(["en"], gpu=False)
    except Exception as exc:
        print(f"EasyOCR warmup failed: {exc}", file=sys.stderr)
        return 1

    print("EasyOCR models are ready.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
