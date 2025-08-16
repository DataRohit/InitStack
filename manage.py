#!/usr/bin/env python
# ruff: noqa: PLC0415

# Standard Library Imports
import os
import sys
from pathlib import Path

# Third Party Imports
from config.opentelemetry import configure_opentelemetry


# Main Function
def main():
    """
    Main Function To Run The Django Management Commands.

    Raises:
        ImportError: If The Django Settings Module Cannot Be Imported.
    """

    # Set The Default Django Settings Module
    os.environ.setdefault(
        key="DJANGO_SETTINGS_MODULE",
        value="config.settings",
    )

    # Configure OpenTelemetry
    configure_opentelemetry()

    try:
        # Import The execute_from_command_line Function From Django.
        from django.core.management import execute_from_command_line

    except ImportError as exc:
        # Set Error Message
        error_message: str = (
            "Django Could Not Be Imported; Ensure It Is Installed, "
            "Available On Your PYTHONPATH, And That Your Virtual Environment Is Activated."
        )

        # Raise The ImportError
        raise ImportError(error_message) from exc

    # Append The Current Path To The Python Path
    current_path: Path = Path(__file__).parent.resolve()
    sys.path.append(str(current_path / "apps"))

    # Execute The Django Management Commands
    execute_from_command_line(sys.argv)


# If The Script Is Run Directly
if __name__ == "__main__":
    # Call The Main Function
    main()
