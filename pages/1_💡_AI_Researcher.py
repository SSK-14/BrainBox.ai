import asyncio
import streamlit as st
from src.modules.model import initialise_model, llm_stream, llm_generate
from src.modules.search import initialise_tavily
from src.modules.utils import init_session_state, get_study_id, study_already_exists, refresh
from src.modules.prompt import search_query_prompt, rag_research_prompt, arxiv_search_prompt
from src.modules.search import ai_search, fetch_arxiv_results
from src.modules.observability import start_trace, end_trace
from src.components.sidebar import side_info
from src.components.ui import example_questions, display_search_result
from src.database.sql_db import insert_study_data, update_study_data
from src.database.vector_db import ingest_knowledge, ingest_document, document_search


async def main():
    st.title("📚 :orange[AI.Researcher]")
    side_info()
    init_session_state()
    initialise_model()

    if st.session_state.title is None:
        col1, col2 = st.columns(2)   
        title = col1.text_input("Create new study ✍🏻", placeholder="Type here...")
        selected_study = col2.selectbox(
            "Add to existing study 🗝️",
            [study['title'] for study in st.session_state.studies],
            index=None,
        )
        if title.strip() != "" or selected_study:
            _, col, _ = st.columns([3, 2, 3])
            if col.button("Start 🧠🍱", use_container_width=True, type="primary"):
                if title.strip() != "":
                    if study_already_exists(title):
                        st.toast("Study with this title already exists. Please choose a different title.")
                        st.stop()
                    st.session_state.title = title
                elif selected_study:
                    study_id = get_study_id(selected_study)
                    st.session_state.title = {"id": study_id, "title": selected_study}
                st.rerun()

    if st.session_state.title:
        if isinstance(st.session_state.title, dict):
            st.header(f":orange[{st.session_state.title['title']}]")
        else:
            st.header(f":orange[{st.session_state.title}]")

    if st.session_state.question is None and st.session_state.title:
        search_type = st.radio("Search Type", ["ArXiv", "Tavily", "Documents"], horizontal=True)
        if search_type:
            st.session_state.search_type = search_type

        if st.session_state.search_type == "Tavily":
            initialise_tavily()

        if st.session_state.search_type == "Documents" and st.session_state.documents == []:
            uploaded_files = st.file_uploader("Upload PDF files", accept_multiple_files=True, type="pdf")
            if uploaded_files:
                ingest_document(uploaded_files)
                st.toast("Documents uploaded successfully.")
        else:     
            example_questions()

        input_question = st.text_area(
            "Enter your research idea 👇",
            placeholder="Type here...",
            help="Add your question in detailed including key points, keywords, and context.",
        )
        _, col, _ = st.columns([3, 2, 3])
        if col.button("Search", type="primary", use_container_width=True):
            if st.session_state.search_type == "Documents" and st.session_state.documents == []:
                st.error("Please upload PDF files.")
                st.stop()
            elif input_question and input_question.strip() == "":
                st.error("Please enter a valid research idea.")
                st.stop()
            else:
                st.session_state.question = input_question
                st.rerun()

    if st.session_state.question:
        st.text_input("Enter your research idea 👇", st.session_state.question)
    
    if st.session_state.question and not st.session_state.search_results and not st.session_state.stream_response:
        with st.spinner("Searching for results..."):
            trace = start_trace("Research", st.session_state.question)
            retrieval = trace.span(name="Retrieval", metadata={"type": st.session_state.search_type}, input=st.session_state.question)
            if st.session_state.search_type == "Tavily":
                search_query = await llm_generate(search_query_prompt(st.session_state.question), "Search Query", trace.id)
                search_results = ai_search(search_query)
            elif st.session_state.search_type == "ArXiv":
                arxiv_request = await llm_generate(arxiv_search_prompt(st.session_state.question), "ArXiv API", trace.id)
                search_results = fetch_arxiv_results(arxiv_request.split('"')[1])
            elif st.session_state.search_type == "Documents":
                search_results = document_search(st.session_state.question)
            else:
                st.error("Invalid search type selected.")
                st.stop()
            
            if search_results:
                retrieval.end(output=search_results)   
                st.session_state.search_results = search_results
                st.rerun()
            else:
                st.error("No search results found. Refresh the page and try again.")
                st.stop()
            
    if st.session_state.search_results:
        if st.session_state.search_type != "Documents":
            display_search_result(st.session_state.search_results)

    if st.session_state.search_type == "Documents" and st.session_state.search_results and not st.session_state.stream_response:
        with st.container(height=400, border=True):
            st.write_stream(llm_stream(rag_research_prompt(st.session_state.question, st.session_state.search_results), "Summary", st.session_state.trace_id))
            st.rerun()

    if st.session_state.deep_dive and st.session_state.search_results and not st.session_state.stream_response:
        with st.container(height=400, border=True):
            search_results = [{result["Title"], result["Summary"]} for result in st.session_state.search_results]
            st.write_stream(llm_stream(rag_research_prompt(st.session_state.question, search_results), "Summary", st.session_state.trace_id))
            st.rerun()

    if  st.session_state.question and st.session_state.stream_response:
        end_trace(st.session_state.stream_response, metadata={"type": st.session_state.search_type})
        with st.container(height=400, border=True):
            st.write(st.session_state.stream_response)
        col1, col2, _ = st.columns([1, 1, 3])
        if col1.button("Save to 🧠🍱", type="primary", use_container_width=True):
            with st.spinner("Saving study to BrainBox. Please wait may take some time... 🕰️"):
                if st.session_state.search_type == "Documents":
                    results = st.session_state.documents
                else:
                    results = [ result["Link"] for result in st.session_state.search_results ]
                
                if isinstance(st.session_state.title, dict):
                    id = st.session_state.title["id"]
                    update_study_data(id, {"results": results,  "summary": st.session_state.stream_response, "type": st.session_state.search_type })
                else:   
                    id = insert_study_data({"title": st.session_state.title, "results": results, "summary": st.session_state.stream_response, "type": st.session_state.search_type})
                ingest_knowledge(id, results, st.session_state.search_type)
                st.toast("Add to knowledge successfully.")
                st.balloons()
                await asyncio.sleep(1.5)
                refresh()
        if col2.button("Clear 🧹", use_container_width=True):
            refresh()

if __name__ == "__main__":
    st.set_page_config(page_title="AI.Researcher", page_icon="✨", layout="wide")
    _, col, _ = st.columns([1, 8, 1])
    with col:
        asyncio.run(main())
