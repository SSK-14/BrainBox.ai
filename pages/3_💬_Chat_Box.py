import asyncio, json
import streamlit as st
from src.modules.model import llm_stream, llm_generate
from src.modules.prompt import followup_query_prompt, rag_prompt
from src.components.sidebar import side_info
from src.components.ui import display_chat_messages
from src.database.vector_db import vector_search

async def main():
    st.title("💬 :blue[Chat]:blue-background[Box]")
    side_info()

    with st.container(height=600, border=False):
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
                with st.expander("Search Results", expanded=True):
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

    if query := st.chat_input("Enter your search query here..."):
        st.session_state.messages.append({"role": "user", "content": query})
        st.rerun()


if __name__ == "__main__":
    st.set_page_config(page_title="Chat Box", page_icon="💬", layout="wide")
    asyncio.run(main())
