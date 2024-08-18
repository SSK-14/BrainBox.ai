import streamlit as st

def side_info():
    with st.sidebar:
        st.logo("src/assets/logo.png", icon_image="src/assets/logo.png", link="https://github.com/SSK-14")
        if "MODEL_API_TOKEN" not in st.secrets:
            st.text_input(
                "Openai API Key",
                type="password",
                placeholder="Paste your api key here",
                help="You can get your API key from https://platform.openai.com/account/api-keys",
                key="model_api_token"
            )
        if "TAVILY_API_KEY" not in st.secrets:
            st.text_input(
                "Tavily API Key",
                type="password",
                placeholder="Paste your tavily key here",
                help="You can get your API key from https://app.tavily.com/home",
                key="tavily_api_key"
            )
        # st.image("src/assets/search.png")
        # st.link_button("🔗 Source Code", "https://github.com/SSK-14/", use_container_width=True)