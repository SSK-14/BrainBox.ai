import streamlit as st
from src.components.sidebar import side_info

def main():
    st.title("👋 Welcome to :orange[BrainBox.AI] 🧠🍱 ")
    side_info()
    card_html = """
        <div style="background-color: rgb(24 11 2); border: 2px solid #d98c00; border-radius: 12px; padding: 0px 16px; width: 100%; box-sizing: border-box; color: white;  font-family: 'Arial', sans-serif; font-size: 16px; color: #FAFAFA; line-height: 1.4; text-align: center;">
            <p>🤖📚 Your AI-powered research assistant that explores the internet 🌐 and research papers 📄 based on your rough idea search queries ✨</p>
        </div>
        """
    st.components.v1.html(card_html, height=90, scrolling=False)
    _, col1, col2, col3, _ = st.columns([2,1,1,1,2])
    col1.page_link("pages/1_💡_AI_Researcher.py", label="AI Researcher", icon="💡", use_container_width=True)
    col2.page_link("pages/2_📚_My_Studies.py", label="My Studies", icon="📚", use_container_width=True)
    col3.page_link("pages/3_💬_Chat_Box.py", label="Chat Box", icon="💬", use_container_width=True)
    col1, col2, col3 = st.columns(3)
    col1.success("**Re-Search:** Utilize Tavily and arXiv APIs to find the most relevant research papers and articles based on your queries.", icon="🔍")
    col2.info("**Knowledge Box:** Store all source results and articles in a vector space for quick and efficient retrieval.", icon="📚")
    col3.warning("**AI Brain:** Use AI as your companion to answer questions, summarize findings, and highlight key points throughout your research.", icon="💡")
    _, col, _ = st.columns([1, 4, 1])
    col.image("src/assets/get_started.png")

if __name__ == "__main__":
    st.set_page_config(page_title="Hello", page_icon="👋", layout="wide")
    _, col, _ = st.columns([1, 8, 1])
    with col:
        main()