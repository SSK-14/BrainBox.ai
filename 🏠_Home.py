import streamlit as st
from src.components.sidebar import side_info
from src.modules.utils import init_session_state
from src.modules.model import initialise_model
from src.modules.search import initialise_tavily

def main():
    st.title("🧠🍱 :blue-background[BrainBox]:blue[.AI]")
    side_info()
    init_session_state()
    initialise_model()
    initialise_tavily()

if __name__ == "__main__":
    st.set_page_config(page_title="Hello", page_icon="👋", layout="wide")
    main()