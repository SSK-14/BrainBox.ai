import streamlit as st
from tavily import TavilyClient

def initialise_tavily():
    if "TAVILY_API_KEY" in st.secrets:
        tavily_api_key = st.secrets["TAVILY_API_KEY"]
    elif "tavily_api_key" in st.session_state and st.session_state.tavily_api_key:
        tavily_api_key = st.session_state.tavily_api_key
    else:
        st.warning('Please provide Tavily API key in the sidebar.', icon="⚠️")
        st.stop()
    st.session_state.tavily_client = TavilyClient(api_key=tavily_api_key)

def ai_search(query, images=False, num_results=10):
    search_result =  st.session_state.tavily_client.search(query, search_depth="advanced", include_images=images, max_results=num_results)
    results = search_result['results']
    return {
        "Select": [False] * len(results),
        "Title": [result['title'] for result in results],
        "Summary": [result['content'] for result in results],
        "Score": [result['score'] for result in results],
        "Link": [result['url'] for result in results]
    }