import asyncio
import streamlit as st
from src.modules.model import initialise_model, llm_stream, llm_generate
from src.modules.search import initialise_tavily
from src.modules.utils import fetch_arxiv_results
from src.modules.prompt import search_query_prompt, search_rag_prompt, arxiv_search_prompt, arxiv_rag_prompt
from src.modules.search import ai_search
from src.components.sidebar import side_info
from src.components.ui import example_questions, display_arxiv_results, display_search_result
from src.database.sql_db import insert_study_data
from src.database.vector_db import ingest_knowledge

async def main():
    st.title("📚 :blue-background[Researcher]:blue[.AI]")
    side_info()

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

    if st.session_state.stream_response and not st.session_state.title:      
        title = st.text_input("Enter title for study ✍🏻", placeholder="Type here...")
        if st.button("Save to BrainBox"):
            if title.strip() == "":
                st.toast("Title cannot be empty.")
            else:
                st.session_state.title = title
                st.rerun()

    if st.session_state.title:
        with st.spinner("Saving study to BrainBox..."):
            if st.session_state.search_type == "Internet search":
                results = [ result["url"] for result in st.session_state.search_results["results"] ]
            else:
                results = [ result["Link"] for result in st.session_state.search_results ]
            id = insert_study_data({"title": st.session_state.title, "results": results, "summary": st.session_state.stream_response, "type": st.session_state.search_type})
            st.toast(f"Study saved successfully with ID: {id}")
            ingest_knowledge(id, results, type)
            st.toast("Add to knowledge successfully.")
            st.balloons()
        
        if st.button("🔍 New Search"):
            st.session_state.search_results = None
            st.session_state.stream_response = None
            st.session_state.question = None
            st.session_state.title = None
            st.session_state.deep_dive = False
            st.rerun()

if __name__ == "__main__":
    st.set_page_config(page_title="AI.Researcher", page_icon="✨", layout="wide")
    asyncio.run(main())
