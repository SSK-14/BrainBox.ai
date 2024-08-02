import asyncio, json
import streamlit as st
from src.modules.model import llm_stream, llm_generate, initialise_model
from src.modules.prompt import followup_query_prompt, rag_prompt
from src.components.sidebar import side_info
from src.components.ui import display_chat_messages, followup_questions
from src.database.vector_db import vector_search
from src.modules.utils import init_session_state

def handle_study_selection():
    st.session_state.chat_ids = [study['id'] for study in st.session_state.studies if study['title'] in st.session_state.study_selection]

async def main():
    st.title("💬 :blue[Chat]:blue-background[Box]")
    side_info()
    init_session_state()
    initialise_model()

    studies_options = [study['title'] for study in st.session_state.studies]
    st.multiselect(
        "Add Studies",
        studies_options,
        [study['title'] for study in st.session_state.studies if study['id'] in st.session_state.chat_ids],
        key="study_selection",
        on_change=handle_study_selection
    )

    with st.container(height=640, border=False):
        display_chat_messages(st.session_state.messages)
            
        search_results = None
        if st.session_state.messages[-1]["role"] != "assistant":
            query = st.session_state.messages[-1]["content"]
            with st.spinner("Searching your knowledge base..."):
                followup_query_asyncio = asyncio.create_task(llm_generate(followup_query_prompt(query)))
                search_results = vector_search(query, st.session_state.chat_ids)
                context = [result["text"] for result in search_results] if search_results else []
                prompt = rag_prompt(st.session_state.messages, context)

            if search_results:
                with st.expander("Search Results", expanded=False):
                    st.json(search_results, expanded=False)

            if followup_query_asyncio:
                followup_query = await followup_query_asyncio
                if followup_query:
                    followup_query = "[" + followup_query.split("[")[1].split("]")[0] + "]"
                    try:
                        st.session_state.followup_query = json.loads(followup_query)
                    except json.JSONDecodeError:
                        st.session_state.followup_query = []

            with st.chat_message("assistant", avatar="🧠"):
                st.write_stream(llm_stream(prompt))
                st.session_state.messages.append({"role": "assistant", "content": st.session_state.stream_response})
                if len(st.session_state.messages) > 1:
                    followup_questions()

    if query := st.chat_input("Enter your search query here..."):
        st.session_state.messages.append({"role": "user", "content": query})
        st.rerun()


if __name__ == "__main__":
    st.set_page_config(page_title="Chat Box", page_icon="💬", layout="wide")
    asyncio.run(main())
