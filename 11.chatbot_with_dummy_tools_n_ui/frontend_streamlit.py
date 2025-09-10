import uuid
import streamlit as st
from langchain_core.messages import HumanMessage
from backend_langgraph import chatbot, get_all_thread_ids

user_avatar = "https://img.icons8.com/ios-filled/50/12B886/user.png"
bot_avatar = "https://img.icons8.com/ios-filled/50/228BE6/sparkling--v1.png"

with open("11.chatbot_with_dummy_tools_n_ui/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

#*******************************UTILITIES********************************#
def generate_thread_id():
    thread_id = str(uuid.uuid4())
    print(f"New chat thread created: {thread_id}")
    return thread_id

def add_thread(thread_id):
    if thread_id not in st.session_state.chat_threads:
        st.session_state.chat_threads.append(thread_id)

def new_conversation():
    st.session_state.thread_id = generate_thread_id()
    add_thread(st.session_state.thread_id)
    st.session_state.message_history = []

def load_conversation(thread_id):
    try:
        return chatbot.get_state(config = {"configurable": {"thread_id": thread_id}}).values["messages"]
    except Exception as e:
        print(f"No messages found for thread_id {thread_id}: {e}")
        return []

def get_chat_title(thread_id):
    messages = load_conversation(thread_id)
    # Find first human message
    first_human = next((msg for msg in messages if getattr(msg, 'type', None) == 'human'), None)
    if not messages:
        return "New Thread"
    elif first_human and getattr(first_human, 'content', None):
        title = first_human.content.strip()[:20]
        return title if title else "New Thread"
    else:
        return "New Thread"

#*******************************SESSION SETUP********************************#
if "message_history" not in st.session_state:
    st.session_state.message_history = []

if "thread_id" not in st.session_state:
    st.session_state.thread_id = generate_thread_id()

if "chat_threads" not in st.session_state:
    st.session_state.chat_threads = get_all_thread_ids()

add_thread(st.session_state.thread_id)

#*******************************SIDEBAR********************************#
with st.sidebar:
    st.markdown("""
        <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined" rel="stylesheet" />
    """, unsafe_allow_html=True)
    st.sidebar.markdown("""<h1 class="my-sidebar-title"><span class="material-symbols-outlined" style="font-size: 32px; vertical-align: middle; color:#4B77D1;">
            action_key
        </span>
        Smart Chatbot</h1>""", unsafe_allow_html=True)
    if st.button("New Conversation", width="stretch", key="new_chat_btn", icon=":material/chat_add_on:", type="tertiary"):
        new_conversation()
        st.rerun()

    st.header("Conversation Threads")

    for thread_id in st.session_state.chat_threads[::-1]:
        chat_title = get_chat_title(thread_id)
        button_label = chat_title if chat_title != "New Thread" else f"New Thread"
        button_icon = ":material/arrow_forward:" if thread_id == st.session_state.thread_id else None
        button_type = "primary" if thread_id == st.session_state.thread_id else "tertiary"
        if st.button(button_label, width="stretch", type=button_type, icon=button_icon):
            st.session_state.thread_id = thread_id
            messages = load_conversation(thread_id)
            st.session_state.message_history = [{"role": msg.type, "content": msg.content} for msg in messages]
            for msg in st.session_state.message_history:
                print(f"After load_conversation Role: {msg['role']}")
            st.rerun()

#******************************LOAD CHAT HISTORY********************************#
for messages in st.session_state.message_history:
    if messages["role"] in ("user", "human"):
        with st.chat_message("user", avatar=user_avatar):
            st.write(messages["content"])
    if messages["role"] in ("assistant", "ai"):
        with st.chat_message("assistant", avatar=bot_avatar):
            st.write(messages["content"])

#*******************************CHAT COMPONENTS********************************#
chatbot_config = {"configurable": {"thread_id": st.session_state.thread_id}}
prompt = st.chat_input(placeholder="type your message here...",)

if prompt:
    st.session_state.message_history.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=user_avatar):
        st.write(prompt)
    placeholder = st.empty()
    with st.spinner("Processing..."):
        result = chatbot.invoke({"messages": [HumanMessage(content=prompt)]}, config=chatbot_config)
        with placeholder.container():
            st.session_state.message_history.append({"role": "assistant", "content": result["messages"][-1].content})
            with st.chat_message("assistant", avatar=bot_avatar):
                st.write(result["messages"][-1].content)
