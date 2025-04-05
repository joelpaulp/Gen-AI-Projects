import streamlit as st
from langchain_ollama import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    AIMessagePromptTemplate,
    ChatPromptTemplate
)

# strea # Suppress deprecation warnings

def initialize_ollama_model():
    try:
        # Test connection first
        import requests
        response = requests.get("http://localhost:11434")
        if response.status_code != 200:
            raise ConnectionError("Ollama server not responding")
            
        llm_engine = ChatOllama(
            model="deepseek-r1:1.5b",
            base_url="http://localhost:11434",
            temperature=0.3
        )
        return llm_engine
    except Exception as e:
        st.error(f"Ollama initialization error: {e}")
        st.error("Please ensure Ollama is running (ollama serve)")
        return None


# Page configuration
st.set_page_config(
    page_title="Virtual Code Assistant",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS with improved visibility
st.markdown("""
    <style>
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
    temperature = st.slider("Creativity", 0.0, 1.0, 0.3, 0.1)

# Initialize LLM
llm_engine = initialize_ollama_model()

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

