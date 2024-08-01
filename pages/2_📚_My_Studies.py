import asyncio, json
import streamlit as st
from src.database.sql_db import fetch_all_studies
from src.components.sidebar import side_info

def display_studies(study):
    with st.container(border=True, height=170):
        col1, col2 = st.columns([4,1])
        col1.subheader(study["title"])
        if col2.button("Add 💬", use_container_width=True, key=f"add_{study['id']}"):
            print("Add Chat")
        st.caption(study['type'])
        col1, col2 = st.columns(2)
        with col1.popover("Source links", use_container_width=True):
            results = json.loads(study["results"])
            for link, index in zip(results, range(len(results))):
                st.write(f"{index+1}. {link}")
        with col2.popover("See summary", use_container_width=True):
            st.write(study["summary"])


async def main():
    st.title("📚 :blue[My.]:blue-background[Studies]")
    side_info()
    st.markdown("---")
    with st.container(height=600, border=False):
        studies = fetch_all_studies()
        if studies:
            col1, col2 = st.columns(2)
            for study, id in zip(studies, range(len(studies))):
                if id % 2 == 0:
                    with col1:
                        display_studies(study)
                else:
                    with col2:
                        display_studies(study)
        else:
            st.error("No studies found.")


if __name__ == "__main__":
    st.set_page_config(page_title="My Studies", page_icon="📚", layout="wide")
    asyncio.run(main())
