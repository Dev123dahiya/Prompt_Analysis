"""Compatibility launcher for the structured golden_response package.

The main implementation lives in the golden_response/ folder. This launcher is
kept at the repository root because the submission checklist asks for a
golden_response.py file.
"""

from golden_response.cli import main


if __name__ == "__main__":
    main()
