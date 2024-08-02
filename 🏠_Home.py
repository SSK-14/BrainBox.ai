import streamlit as st
from src.components.sidebar import side_info

def main():
    st.title("🧠🍱 :blue-background[BrainBox]:blue[.AI]")
    side_info()

if __name__ == "__main__":
    st.set_page_config(page_title="Hello", page_icon="👋", layout="wide")
    main()