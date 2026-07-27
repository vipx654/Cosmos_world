"""
===============================================================================
COSMOS Workspace Navigator

Professional navigation component for the COSMOS Trading Operating System.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

import gradio as gr


def create_sidebar() -> None:
    """
    Render the COSMOS workspace navigator.

    This component is responsible only for application navigation.
    """

    with gr.Column(scale=1, min_width=240):

        gr.Markdown("# 🌌 COSMOS")

        gr.Markdown("### Trading Operating System")

        gr.Markdown("---")

        gr.Button(
            "🏠 Dashboard",
            variant="primary",
            size="lg",
        )

        gr.Button("📈 Markets")

        gr.Button("🎯 Trade Workspace")

        gr.Button("🤖 AI Assistant")

        gr.Button("📊 Scanner")

        gr.Button("📑 Journal")

        gr.Button("💼 Portfolio")

        gr.Button("📰 News")

        gr.Button("⚙ Settings")

        gr.Markdown("---")

        gr.Markdown(
            """
### Workspace

🟢 Professional Mode

Version 1.0.0
"""
        )
