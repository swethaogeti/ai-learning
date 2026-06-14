import streamlit as st
from model_engine import generate_cloud_response

st.set_page_config(page_title="Cloud Production Chatbot", page_icon="☁️")
st.title("☁️ Industrial Standard Cloud AI")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

if prompt := st.chat_input("Send a message over the cloud..."):
    with st.chat_message("user"):
        st.write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        
        # Stream directly from our updated Google Cloud engine
        for chunk in generate_cloud_response(st.session_state.messages):
            full_response += chunk
            response_placeholder.write(full_response + "▌")
            
        response_placeholder.write(full_response)
        
    st.session_state.messages.append({"role": "assistant", "content": full_response})