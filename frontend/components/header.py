"""
COSMOS Header Component

Provides the global application header.

Author: COSMOS Development Team
License: MIT
"""

from __future__ import annotations

import gradio as gr

from config import APP_NAME, APP_VERSION


def create_header() -> None:
    """
    Render the COSMOS application header.
    """

    with gr.Row(equal_height=True):

        gr.Markdown(
            f"""
# 🌌 {APP_NAME}

**AI-Native Trading Operating System**

Version **{APP_VERSION}**
"""
        )

        gr.Markdown(
            """
### 🟢 System Status

Broker: Offline

AI: Initializing

Database: Offline
"""
        )
