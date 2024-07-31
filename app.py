import asyncio
import streamlit as st
from src.modules.model import initialise_model, llm_stream, llm_generate
from src.modules.search import initialise_tavily
from src.modules.utils import init_session_state, fetch_arxiv_results
from src.modules.prompt import search_query_prompt, search_rag_prompt, arxiv_search_prompt, arxiv_rag_prompt
from src.modules.search import ai_search
from src.components.sidebar import side_info
from src.components.ui import example_questions, display_arxiv_results, display_search_result

async def main():
    st.title("📚 :blue-background[BrainBox]:blue[.ai]")
    init_session_state()
    side_info()
    initialise_model()
    initialise_tavily()

    if st.session_state.question is None:
        search_type = st.radio("Search Type", ["Internet search", "ArXiv search"], horizontal=True)
        if search_type:
            st.session_state.search_type = search_type
        input_question = st.text_area(
            "Enter your research idea 👇",
            placeholder="Type here...",
            help="Add your question in detailed including key points, keywords, and context.",
        )
        if input_question:
            st.session_state.question = input_question
            st.rerun()
        example_questions()

    if st.session_state.question:
        st.text_input("Enter your research idea 👇", st.session_state.question)
    
    if st.session_state.question and not st.session_state.search_results and not st.session_state.stream_response:
        with st.spinner("Searching for results..."):
            if st.session_state.search_type == "Internet search":
                # search_query = llm_generate(search_query_prompt(st.session_state.question))
                search_results = ai_search(st.session_state.question)
                if search_results["results"]:
                    st.session_state.search_results = search_results
                    st.rerun()
                else:
                    st.error("No search results found. Refresh the page and try again.")
                    st.stop()
            elif st.session_state.search_type == "ArXiv search":
                arxiv_request = llm_generate(arxiv_search_prompt(st.session_state.question))
                st.session_state.search_results = fetch_arxiv_results(arxiv_request.split('"')[1])
                st.rerun()
            else:
                st.error("Invalid search type selected.")
                st.stop()
            
    if st.session_state.search_results:
        if st.session_state.search_type == "ArXiv search":
            display_arxiv_results(st.session_state.search_results)
        else:
            display_search_result(st.session_state.search_results)

    if st.session_state.search_type == "Internet search" and st.session_state.search_results and not st.session_state.stream_response:
        with st.container(height=400, border=True):
            search_results = [result["content"][:300] for result in st.session_state.search_results["results"]]
            st.write_stream(llm_stream(search_rag_prompt(st.session_state.question, search_results)))
            st.rerun()

    if st.session_state.deep_dive and st.session_state.search_results and not st.session_state.stream_response:
        with st.container(height=400, border=True):
            search_results = [{result["Title"], result["Summary"]} for result in st.session_state.search_results]
            st.write_stream(llm_stream(arxiv_rag_prompt(st.session_state.question, search_results)))
            st.rerun()

    if st.session_state.stream_response:
        with st.container(height=400, border=True):
            st.write(st.session_state.stream_response)


if __name__ == "__main__":
    st.set_page_config(page_title="AI.Researcher", page_icon="✨", layout="wide")
    asyncio.run(main())
