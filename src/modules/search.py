import streamlit as st
from tavily import TavilyClient
import requests
import xml.etree.ElementTree as ET
from datetime import datetime

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

def fetch_arxiv_results(api_url):
    response = requests.get(api_url)
    response.raise_for_status()
    root = ET.fromstring(response.content)
    results = []
    for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
        title = entry.find('{http://www.w3.org/2005/Atom}title').text
        summary = entry.find('{http://www.w3.org/2005/Atom}summary').text
        authors = [author.find('{http://www.w3.org/2005/Atom}name').text for author in entry.findall('{http://www.w3.org/2005/Atom}author')]
        link = entry.find('{http://www.w3.org/2005/Atom}id').text
        published = entry.find('{http://www.w3.org/2005/Atom}published').text
        results.append({
            'title': title,
            'summary': summary,
            'authors': authors,
            'link': link,
            'published': published
        })
    return {
        "Select": [False] * len(results),
        "Title": [result['title'] for result in results],
        "Summary": [result['summary'] for result in results],
        "Published": [datetime.strptime(result['published'], "%Y-%m-%dT%H:%M:%SZ").strftime("%d/%m/%Y") for result in results],
        "Authors": [', '.join(result['authors']) for result in results],
        "Link": [result['link'] for result in results]
    }