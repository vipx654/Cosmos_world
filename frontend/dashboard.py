"""
===============================================================================
COSMOS Dashboard

Main dashboard layout for the COSMOS Trading Operating System.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

import gradio as gr

from frontend.components.header import create_header
from frontend.components.sidebar import create_sidebar
from frontend.components.statusbar import create_statusbar
from frontend.components.workspace import create_workspace
from frontend.components.ai_panel import create_ai_panel
from frontend.components.market_panel import create_market_panel
from frontend.components.portfolio_panel import create_portfolio_panel
from frontend.components.notifications import create_notifications


def create_dashboard() -> gr.Blocks:
    """
    Create and return the COSMOS dashboard.
    """

    with gr.Blocks(
        title="COSMOS",
        fill_height=True,
    ) as dashboard:

        # ---------------------------------------------------------------------
        # Header
        # ---------------------------------------------------------------------
        create_header()

        # ---------------------------------------------------------------------
        # Main Workspace
        # ---------------------------------------------------------------------
        with gr.Row():

            create_sidebar()

            with gr.Column(scale=8):

                create_workspace()

                with gr.Row():

                    create_market_panel()

                    create_portfolio_panel()

                    create_notifications()

            create_ai_panel()

        # ---------------------------------------------------------------------
        # Status Bar
        # ---------------------------------------------------------------------
        create_statusbar()

    return dashboard
