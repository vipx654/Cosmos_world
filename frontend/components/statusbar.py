"""
===============================================================================
COSMOS Status Bar

Global application status component.

Displays the health and runtime status of the COSMOS platform.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

import gradio as gr


def create_statusbar() -> None:
    """
    Render the global application status bar.
    """

    with gr.Row(equal_height=True):

        gr.Markdown(
            """
🟢 **Broker:** Offline
"""
        )

        gr.Markdown(
            """
🤖 **AI:** Initializing
"""
        )

        gr.Markdown(
            """
🗄 **Database:** Offline
"""
        )

        gr.Markdown(
            """
🌍 **Market:** Closed
"""
        )

        gr.Markdown(
            """
📡 **Latency:** --
"""
        )

        gr.Markdown(
            """
🕒 **UTC:** --
"""
        )
