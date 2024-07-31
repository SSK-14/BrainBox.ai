import streamlit as st
from src.modules.model import model_options

def side_info():
    with st.sidebar:
        st.logo("src/assets/ssk.png", icon_image="src/assets/ssk.png", link="https://github.com/SSK-14")
        st.image("src/assets/logo.png")
        if "TAVILY_API_KEY" not in st.secrets:
            st.text_input(
                "Tavily API Key",
                type="password",
                placeholder="Paste your tavily key here",
                help="You can get your API key from https://app.tavily.com/home",
                key="tavily_api_key"
            ) 
        st.sidebar.selectbox("Select a model", list(model_options.keys()), key="model_name")
        st.markdown("---")
        st.image("src/assets/search.png")
        st.link_button("🔗 Source Code", "https://github.com/SSK-14/", use_container_width=True)