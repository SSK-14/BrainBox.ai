import os
import streamlit as st
from langfuse import Langfuse

os.environ["LANGFUSE_SECRET_KEY"] = st.secrets["LANGFUSE_SECRET_KEY"]
os.environ["LANGFUSE_PUBLIC_KEY"] = st.secrets["LANGFUSE_PUBLIC_KEY"]
os.environ["LANGFUSE_HOST"] = "https://cloud.langfuse.com" 

langfuse = Langfuse()

def start_trace(name, query):
    trace = langfuse.trace(name=name, input=query)
    st.session_state.trace_id = trace.id
    return trace

def end_trace(output, metadata=None):
    langfuse.trace(id=st.session_state.trace_id, output=output, metadata=metadata)

def add_feedback(value, comment=None):
    langfuse.score(
        trace_id=st.session_state.trace_id,
        name="user-explicit-feedback",
        value=value,
        comment=comment
    )