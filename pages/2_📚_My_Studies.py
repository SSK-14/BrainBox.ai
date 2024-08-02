import asyncio, json
import streamlit as st
from src.components.sidebar import side_info
from src.modules.utils import init_session_state

def display_studies(study):
    with st.container(border=True, height=112):
        col1, col2 = st.columns([4,1])
        col1.markdown(f"##### :blue-background[{study['title']}]")
        col2.caption(f"{study['type']}")
        col1, col2, col3 = st.columns([3,3,2])
        with col1.popover("Source links", use_container_width=True):
            results = json.loads(study["results"])
            for link, index in zip(results, range(len(results))):
                st.write(f"{index+1}. {link}")
        with col2.popover("See summary", use_container_width=True):
            st.write(study["summary"])
        if col3.button(f"{ 'Remove' if study['id'] in st.session_state.chat_ids else 'Add'} 💬", use_container_width=True, key=f"add_{study['id']}", type="primary"):
            if study["id"] in st.session_state.chat_ids:
                st.session_state.chat_ids.remove(study["id"])
            else:
                st.session_state.chat_ids.append(study["id"])
            st.rerun()

async def main():
    st.title("📚 :blue[My.]:blue-background[Studies]")
    side_info()
    init_session_state()
    st.markdown("---")
    with st.container(height=600, border=False):
        if st.session_state.studies:
            col1, col2 = st.columns(2)
            for study, id in zip(st.session_state.studies, range(len(st.session_state.studies))):
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
