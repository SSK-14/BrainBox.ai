import asyncio
import streamlit as st
from src.modules.model import initialise_model, llm_stream, llm_generate
from src.modules.search import initialise_tavily
from src.modules.utils import init_session_state
from src.modules.prompt import search_query_prompt, search_rag_prompt
from src.modules.search import ai_search
from src.components.sidebar import side_info
from src.components.ui import example_questions

async def main():
    st.title("#️⃣ AI.:blue[Researcher]")
    init_session_state()
    side_info()
    initialise_model()
    initialise_tavily()

    if st.session_state.question is None:
        input_question = st.text_area(
            "Enter your research idea 👇",
            placeholder="Type here...",
            help="Add your question in detailed including key points, keywords, and context.",
        )
        if input_question:
            st.session_state.question = input_question
            st.rerun()
        example_questions()
    
    if st.session_state.question and not st.session_state.stream_response:
        search_query = llm_generate(search_query_prompt(st.session_state.question))
        st.write(search_query)
        search_results = ai_search(search_query)
        if search_results["results"]:
            st.write(search_results["results"])
            st.write_stream(llm_stream(search_rag_prompt(st.session_state.question, search_results)))
            st.rerun()

    if st.session_state.stream_response:
        st.write(st.session_state.stream_response)


if __name__ == "__main__":
    st.set_page_config(page_title="AI.Researcher", page_icon="✨")
    asyncio.run(main())
