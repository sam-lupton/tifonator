"""Gradio UI — entry point for non-technical users."""

from __future__ import annotations
import gradio as gr


def main() -> None:
    with gr.Blocks(title="Tifonator") as demo:
        gr.Markdown("# Tifonator\nGenerate a Tifo-style football podcast episode.")
    demo.launch()


if __name__ == "__main__":
    main()
