"""
===============================================================================
COSMOS Market Intelligence Panel

Displays real-time market intelligence, session information, and watchlists.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

import gradio as gr


def create_market_panel() -> None:
    """
    Render the market intelligence panel.
    """

    with gr.Column(scale=2):

        gr.Markdown("# 🌍 Market Intelligence")

        gr.Markdown("## 🌐 Market Session")

        gr.Markdown("""
• Sydney : Closed

• Tokyo : Closed

• London : Closed

• New York : Closed
""")

        gr.Markdown("---")

        gr.Markdown("## ⭐ Watchlist")

        gr.Dataframe(
            headers=[
                "Symbol",
                "Price",
                "Change",
            ],
            value=[
                ["EURUSD", "--", "--"],
                ["GBPUSD", "--", "--"],
                ["USDJPY", "--", "--"],
                ["XAUUSD", "--", "--"],
                ["BTCUSD", "--", "--"],
            ],
            interactive=False,
            wrap=True,
        )

        gr.Markdown("---")

        gr.Markdown("## ⚡ Scanner")

        gr.Markdown("""
• Liquidity Sweep

• Order Block

• Fair Value Gap

• Market Structure

• BOS / CHOCH

• Volume Spike
""")
