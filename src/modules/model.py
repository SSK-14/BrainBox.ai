import streamlit as st
from langfuse.openai import OpenAI

model_options = {
    "Falcon 180B": "tiiuae/falcon-180b-chat",
    "Falcon 11B": "tiiuae/falcon-11b",
}

def initialise_model():
    if "llm" not in st.session_state:
        st.session_state.llm = None
    if "MODEL_API_TOKEN" in st.secrets:
        model_api_token = st.secrets['MODEL_API_TOKEN']
        st.session_state.model_api_token = model_api_token
    if "model_api_token" not in st.session_state or not st.session_state.model_api_token:
        st.warning('Please provide Model API key in secrets.', icon="⚠️")
        st.stop()
    st.session_state.llm = OpenAI(
        api_key=st.session_state.model_api_token,
        base_url="https://api.ai71.ai/v1/",
    )

async def llm_generate(prompt, name="AI Generate", trace_id=None):
    completion = st.session_state.llm.chat.completions.create(
        model=model_options[st.session_state.model_name] or "tiiuae/falcon-180b-chat", 
        messages=prompt,
        name=name,
        trace_id=trace_id,
    )
    return completion.choices[0].message.content

def llm_stream(prompt, name="AI Stream", trace_id=None):
    st.session_state.stream_response = ""
    stream = st.session_state.llm.chat.completions.create(
        model=model_options[st.session_state.model_name] or "tiiuae/falcon-180b-chat", 
        messages=prompt,
        stream=True,
        name=name,
        trace_id=trace_id,
    )
    for chunk in stream:
        st.session_state.stream_response += str(chunk.choices[0].delta.content or "")
        yield str(chunk.choices[0].delta.content or "")
