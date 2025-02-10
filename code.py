import os
import streamlit as st

# Set the port from the environment variable
port = int(os.getenv("PORT", 8501))

# Your existing code...

if __name__ == "__main__":
    st.run(port=port)
from langchain_ollama import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    AIMessagePromptTemplate,
    ChatPromptTemplate
)

# Page configuration
st.set_page_config(
    page_title="Virtual Code Assistant",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS with improved visibility
st.markdown("""
    <style>
        /* Body background */
        .main {
            background-color: #f0f2f6;
            padding: 2rem;
        }
        
        /* Headers */
        .css-10trblm {
            color: #1E88E5;
            font-size: 2.5rem !important;
            font-weight: 600 !important;
        }
        
        /* Sidebar */
        .css-1d391kg {
            padding: 2rem 1rem;
        }
        
        /* Chat container */
        .stChatMessageContent {
            background-color: #475494;
            border-radius: 10px;
            padding: 1rem;
            margin: 0.5rem 0;
            color: #0f172a;  /* Dark text color for contrast */
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
        }
        
        /* User message */
        .stChatMessage[data-testid="user-message"] .stChatMessageContent {
            background-color: #e3f2fd;
            color: #0f172a;
        }
        
        /* AI message */
        .stChatMessage[data-testid="assistant-message"] .stChatMessageContent {
            background-color: #475494;
            color: #0f172a;
        }
        
        /* Chat input box */
        .stChatInput {
            background-color: #475494;
            border-radius: 20px;
            padding: 0.5rem;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
        }
        
        /* Code blocks in messages */
        code {
            background-color: #f8f9fa !important;
            padding: 0.2em 0.4em !important;
            border-radius: 3px !important;
            color: #1a1a1a !important;
        }
    </style>
""", unsafe_allow_html=True)

# Main title with minimal design
col1, col2, col3 = st.columns([1,2,1])
with col2:
    st.title("Code Assistant")
    st.caption("Professional AI Pair Programming")

# Sidebar configuration
with st.sidebar:
    st.header("Settings")
    selected_model = st.selectbox(
        "Model",
        ["deepseek-r1:1.5b", "deepseek-r1:1.5b"],
        index=0
    )
    temperature = st.slider("Temperature", 0.0, 1.0, 0.3, 0.1)

# Initialize LLM
llm_engine = ChatOllama(
    model=selected_model,
    base_url="http://localhost:11434",
    temperature=temperature
)

# System prompt focused on direct answers
system_prompt = SystemMessagePromptTemplate.from_template(
    "You are a professional coding assistant. Provide only direct, implementable solutions "
    "without explanations unless specifically asked. Focus on clean, efficient code."
)

# Initialize message log
if "message_log" not in st.session_state:
    st.session_state.message_log = [{"role": "ai", "content": "How can I help you with your code today?"}]

# Display chat messages
for message in st.session_state.message_log:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

def generate_ai_response(prompt_chain):
    processing_pipeline = prompt_chain | llm_engine | StrOutputParser()
    return processing_pipeline.invoke({})

def build_prompt_chain():
    prompt_sequence = [system_prompt]
    for msg in st.session_state.message_log:
        if msg["role"] == "user":
            prompt_sequence.append(HumanMessagePromptTemplate.from_template(msg["content"]))
        elif msg["role"] == "ai":
            prompt_sequence.append(AIMessagePromptTemplate.from_template(msg["content"]))
    return ChatPromptTemplate.from_messages(prompt_sequence)

# Chat input
user_query = st.chat_input("Type your code question...")

if user_query:
    st.session_state.message_log.append({"role": "user", "content": user_query})
    
    with st.chat_message("user"):
        st.markdown(user_query)
    
    with st.chat_message("ai"):
        with st.spinner("Processing..."):
            prompt_chain = build_prompt_chain()
            ai_response = generate_ai_response(prompt_chain)
            st.markdown(ai_response)
    
    st.session_state.message_log.append({"role": "ai", "content": ai_response})