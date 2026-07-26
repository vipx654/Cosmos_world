import gradio as gr
from config import APP_NAME, APP_VERSION, AI_NAME


def dashboard():
    with gr.Blocks(
        title=APP_NAME,
        theme=gr.themes.Soft(),
    ) as app:

        gr.Markdown(
            f"""
# 🌌 {APP_NAME}
### AI-Native Trading Operating System

**Version:** {APP_VERSION}
"""
        )

        with gr.Row():

            with gr.Column(scale=1):
                gr.Markdown("## 📂 Navigation")

                gr.Button("🏠 Dashboard")
                gr.Button("📈 Trade Intelligence")
                gr.Button("🤖 AI Assistant")
                gr.Button("💼 Portfolio")
                gr.Button("📊 Market Watch")
                gr.Button("🔌 Connectors")
                gr.Button("⚙️ Settings")

            with gr.Column(scale=3):

                gr.Markdown("## 📊 Dashboard")

                gr.Info("Welcome to COSMOS.")

                gr.Markdown("""
### System Status

- ✅ Dashboard Ready
- ✅ Architecture Complete
- ✅ Repository Ready
- 🚧 AI Engine (Coming Soon)
- 🚧 MT5 Connector (Coming Soon)
- 🚧 Binance Connector (Coming Soon)
                """)

            with gr.Column(scale=1):

                gr.Markdown(f"## 🤖 {AI_NAME}")

                chatbot = gr.Chatbot(
                    height=400,
                    label="AI Assistant"
                )

                msg = gr.Textbox(
                    placeholder="Ask COSMOS..."
                )

                gr.Button("Send")

    return app


app = dashboard()

if __name__ == "__main__":
    app.launch()
