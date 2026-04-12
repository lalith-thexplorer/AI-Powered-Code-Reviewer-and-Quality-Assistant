"""Shared Groq credential helpers for local and hosted runtimes."""

from __future__ import annotations

import os

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional during deployment
    load_dotenv = None


if load_dotenv is not None:
    load_dotenv()


def get_groq_api_key() -> str:
    """Return the Groq API key from env vars or Streamlit secrets."""
    api_key = os.environ.get("GROQ_API_KEY")
    if api_key:
        return api_key

    try:
        import streamlit as st

        if "GROQ_API_KEY" in st.secrets:
            secret_value = st.secrets["GROQ_API_KEY"]
            if secret_value:
                return str(secret_value)
    except Exception:
        pass

    raise RuntimeError(
        "GROQ_API_KEY is not configured. Set it as an environment variable or in Streamlit secrets."
    )