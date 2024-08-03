import streamlit as st
from src.database.sql_db import fetch_all_studies
import requests
import xml.etree.ElementTree as ET
import pandas as pd
from datetime import datetime

def init_session_state():
    state_defaults = {
        "stream_response": None,
        "search_results": None,
        "question": None,
        "deep_dive": False,
        "title": None,
        "studies": fetch_all_studies(),
        "chat_ids": [],
        "messages": [{"role": "assistant", "content": "Hi. I'm BrainBox.AI your super-smart AI assistant. Ask me anything you are looking for from your studies 🪄."}],
        "followup_query": []
    }
    for key, value in state_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

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

def get_study_id(study_title):
    study_id = None
    for study in st.session_state.studies:
        if study["title"] == study_title:
            study_id = study["id"]
            break
    return study_id

def study_already_exists(study_title):
    for study in st.session_state.studies:
        if study["title"] == study_title:
            return True
    return False


def handle_study_selection():
    st.session_state.chat_ids = [study['id'] for study in st.session_state.studies if study['title'] in st.session_state.study_selection]
