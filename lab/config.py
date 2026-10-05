import os
from pathlib import Path
from dotenv import load_dotenv
ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

def setting(name, default=""):
    if os.getenv("LAB_OFFLINE") == "1":
        return default
    if os.getenv(name):
        return os.environ[name]
    try:
        import streamlit as st
        return str(st.secrets.get(name, default))
    except (FileNotFoundError, KeyError):
        return default

def configured(*names):
    return all(setting(name) for name in names)
