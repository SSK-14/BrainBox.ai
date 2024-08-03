import streamlit as st
from src.components.sidebar import side_info

def main():
    st.title("👋 Welcome to :blue-background[BrainBox]:blue[.AI] 🧠🍱 ")
    side_info()
    card_html = """
        <div style="background-color: #002033; border: 2px solid #6a89a5; border-radius: 12px; padding: 0px 16px; width: 100%; box-sizing: border-box; color: white;  font-family: 'Arial', sans-serif; font-size: 15px; color: #FAFAFA; line-height: 1.4;">
            <p>🤖📚 Your AI-powered research assistant that explores the internet 🌐 and research papers 📄 based on your rough idea search queries ✨</p>
        </div>
        """
    st.components.v1.html(card_html, height=100, scrolling=False)
    _, col1, col2, col3, _ = st.columns([2,1,1,1,2])
    col1.page_link("pages/1_💡_AI_Researcher.py", label="AI Researcher", icon="💡", use_container_width=True)
    col2.page_link("pages/2_📚_My_Studies.py", label="My Studies", icon="📚", use_container_width=True)
    col3.page_link("pages/3_💬_Chat_Box.py", label="Chat Box", icon="💬", use_container_width=True)
    st.markdown("---")
    st.subheader("Powered by 🤖🧠")
    col, _ = st.columns([1,3])
    col.image("src/assets/search.png")
    st.link_button("🔗 Source Code", "https://github.com/SSK-14/")

if __name__ == "__main__":
    st.set_page_config(page_title="Hello", page_icon="👋", layout="wide")
    _, col, _ = st.columns([1, 8, 1])
    with col:
        main()