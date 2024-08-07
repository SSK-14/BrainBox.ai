import asyncio, json
import streamlit as st
from src.modules.model import llm_stream, llm_generate, initialise_model
from src.modules.prompt import followup_query_prompt, rag_prompt, rag_check_prompt, standalone_query_prompt
from src.modules.observability import start_trace, end_trace, add_feedback
from src.modules.utils import init_session_state, handle_study_selection, clear_chat_history
from src.components.sidebar import side_info
from src.components.ui import display_chat_messages, followup_questions, display_chat_results
from src.database.vector_db import vector_search

async def main():
    st.title("💬 :orange[ChatBox]")
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
            
        if st.session_state.messages[-1]["role"] != "assistant":
            st.session_state.chat_search_results = None
            st.session_state.followup_query = None
            st.session_state.feedback = None
            query = st.session_state.messages[-1]["content"]
            trace = start_trace("ChatBox", query)
            with st.spinner("Searching your knowledge base..."):
                retrieval = trace.span(name="Retrieval", metadata={"filter": st.session_state.chat_ids}, input=query)
                if len(st.session_state.messages) > 2:
                    query = await llm_generate(standalone_query_prompt(query, st.session_state.messages), "Standalone Question", trace.id)
                followup_query_asyncio = asyncio.create_task(llm_generate(followup_query_prompt(query), "Follow up question", trace.id))
                if st.session_state.chat_ids != []:
                    filter = {"id": {"$in": st.session_state.chat_ids}}
                else:
                    filter = None
                st.session_state.chat_search_results = vector_search(query, filter, re_rank=True)
                source_check = await llm_generate(rag_check_prompt(query, st.session_state.chat_search_results), "RAG Check", trace.id)
                if "no" in source_check.lower():
                    st.session_state.chat_search_results = None
                retrieval.end(output=st.session_state.chat_search_results)
                context = [result["text"] for result in st.session_state.chat_search_results] if st.session_state.chat_search_results else None
                prompt = rag_prompt(st.session_state.messages, context)

            if followup_query_asyncio:
                followup_query = await followup_query_asyncio
                if followup_query:
                    followup_query = "[" + followup_query.split("[")[1].split("]")[0] + "]"
                    try:
                        st.session_state.followup_query = json.loads(followup_query)
                    except json.JSONDecodeError:
                        st.session_state.followup_query = []

            with st.chat_message("assistant", avatar="🧠"):
                st.write_stream(llm_stream(prompt, "Answer", trace.id))
                end_trace(st.session_state.stream_response)
                st.session_state.messages.append({"role": "assistant", "content": st.session_state.stream_response})
        
        if st.session_state.chat_search_results:
            display_chat_results(st.session_state.chat_search_results)   
        
        if len(st.session_state.messages) > 1:
            col1, _, col2 = st.columns([1, 3, 1])
            col1.button('New Chat', on_click=clear_chat_history)
            with col2:
                if st.session_state.feedback is None:
                    st.session_state.feedback = st.feedback(options="faces")
                    if st.session_state.feedback:
                        add_feedback(st.session_state.feedback)
            followup_questions()

    if query := st.chat_input("Enter your search query here..."):
        st.session_state.messages.append({"role": "user", "content": query})
        st.rerun()


if __name__ == "__main__":
    st.set_page_config(page_title="Chat Box", page_icon="💬")
    asyncio.run(main())
