import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from backend_langgraph import chatbot


chatbot_config = {"configurable": {"thread_id": "thread1"}}

if "message_history" not in st.session_state:
    st.session_state.message_history = []

for msg in st.session_state.message_history:
    st.chat_message(msg["role"]).write(msg["content"])

prompt = st.chat_input(placeholder="type your message here...")

if prompt:
    st.session_state.message_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)
    placeholder = st.empty()
    with st.spinner("Processing..."):
        result = chatbot.invoke({"messages": [HumanMessage(content=prompt)]}, config=chatbot_config)
        with placeholder.container():
            st.session_state.message_history.append({"role": "assistant", "content": result["messages"][-1].content})
            with st.chat_message("assistant"):
                st.write(result["messages"][-1].content)