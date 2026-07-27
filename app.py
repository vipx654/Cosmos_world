"""
COSMOS
AI-Native Trading Operating System

Application Entry Point

Author: COSMOS Development Team
License: MIT
"""

from frontend.dashboard import create_dashboard


def main() -> None:
    """
    Application entry point.

    Initializes and launches the COSMOS dashboard.
    """

    app = create_dashboard()

    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        show_error=True,
    )


if __name__ == "__main__":
    main()
