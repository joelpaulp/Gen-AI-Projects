import streamlit as st
from langchain_ollama import ChatOllama
from langchain_core.output_parsers import StrOutputParser

from langchain_core.prompts import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    AIMessagePromptTemplate,
    ChatPromptTemplate
)


st.title("DeepSeek Code Companion")
st.caption("Your AI Pair Programmer with Debugging Superpowers")
with st.sidebar:
    st.header("Configuration")
    selected_model =st.selectbox(
        "Choose Model",
        ["deepseek-r1:1.5b","deepseek-r1:1.5b"],
        index=0
    )
st.divider()


llm_engine = ChatOllama(
    model = selected_model,
    base_url="http://localhost:11434",
    temperature=0.3
)

system_prompt = SystemMessagePromptTemplate.from_template(
    "You are an expert AI coding assistant, providing concise, correct solutions"
    "with strategic print statements for debugging always respond in english."
)


if "message_log" not in st.session_state:
    st.session_state.message_log = [{"role":"ai","content":"Hi! i'm Deepseek AI how may i help you?"}]

    chat_container =st.container()

    with chat_container:
        for message in st.session_state.message_log:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

user_query = st.chat_input("Type your coding question here...")

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

if user_query:
    st.session_state.message_log.append({"role":"user","content":user_query})

    with st.spinner("Processing..."):
        prompt_chain = build_prompt_chain()
        ai_response = generate_ai_response(prompt_chain)

    st.session_state.message_log.append({"role":"ai","content": ai_response})

    st.rerun()
    
       