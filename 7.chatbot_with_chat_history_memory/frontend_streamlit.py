import uuid
import streamlit as st
from langchain_core.messages import HumanMessage
from backend_langgraph import chatbot

st.title("Chatbot with Chat History-DB")

#*******************************UTILITIES********************************#
def generate_thread_id():
    thread_id = str(uuid.uuid4())
    print(f"New chat thread created: {thread_id}")
    return thread_id

def add_thread(thread_id):
    if thread_id not in st.session_state.chat_threads:
        st.session_state.chat_threads.append(thread_id)

def new_chat():
    st.session_state.thread_id = generate_thread_id()
    add_thread(st.session_state.thread_id)
    st.session_state.message_history = []


def load_conversation(thread_id):
    try:
        return chatbot.get_state(config = {"configurable": {"thread_id": thread_id}}).values["messages"]
    except Exception as e:
        print(f"Error loading conversation for thread {thread_id}: {e}")
        return []

#*******************************SESSION SETUP********************************#
if "message_history" not in st.session_state:
    st.session_state.message_history = []

if "thread_id" not in st.session_state:
    st.session_state.thread_id = generate_thread_id()

if "chat_threads" not in st.session_state:
    st.session_state.chat_threads = []

add_thread(st.session_state.thread_id)

#*******************************SIDEBAR********************************#
with st.sidebar:
    if st.button("New Chat", type="primary", width="stretch"):
        new_chat()
        st.rerun()

    st.header("Conversation Threads")

    for thread_id in st.session_state.chat_threads[::-1]:
        if thread_id == st.session_state.thread_id:
            if st.button(thread_id, type="primary", width="stretch"):
                st.session_state.thread_id = thread_id
                messages = load_conversation(thread_id)
                st.session_state.message_history = [{"role": msg.type, "content": msg.content} for msg in messages]
                st.rerun()
        else:
            if st.button(thread_id, type="secondary", width="stretch"):
                st.session_state.thread_id = thread_id
                messages = load_conversation(thread_id)
                st.session_state.message_history = [{"role": msg.type, "content": msg.content} for msg in messages]
                st.rerun()


#******************************LOAD CHAT HISTORY********************************#
for messages in st.session_state.message_history:
    st.chat_message(messages["role"]).write(messages["content"])

#*******************************CHAT COMPONENTS********************************#
chatbot_config = {"configurable": {"thread_id": st.session_state.thread_id}}
prompt = st.chat_input(placeholder="type your message here...",)

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
