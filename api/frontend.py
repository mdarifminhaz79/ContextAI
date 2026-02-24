import streamlit as st
import requests

API_BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="ContextAI - Creator Assistant", page_icon="🤖")

st.title("🤖 ContextAI: Smart YouTube Assistant")
st.markdown('Process your video and Generate smart reply using AI')


with st.sidebar:
    st.header("Video Setup")
    video_url = st.text_input("Enter YouTube URL:")
    if st.button("Process Video"):
        if video_url:
            with st.spinner('Processing video (Downloading + Transcribing)...'):
                response = requests.post(f"{API_BASE_URL}/process-video/",json={'url':video_url})
                if response.status_code == 200:
                    st.success('Video processed successfully!')
                else:
                    st.error('Error processing video.')
        else:
            st.warning('Please enter a URL.')


# মেইন এরিয়া - চ্যাট ইন্টারফেস
st.header("2. AI Reply Generator")

# সেশন স্টেট ব্যবহার করে চ্যাট হিস্ট্রি রাখা
if "messages" not in st.session_state:
    st.session_state.messages = []

# আগের মেসেজগুলো দেখানো
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ইউজার ইনপুট
if user_comment := st.chat_input("Write a viewer's comment here..."):
    # ইউজারের কমেন্ট দেখানো
    st.session_state.messages.append({"role": "user", "content": user_comment})
    with st.chat_message("user"):
        st.markdown(user_comment)

    # এপিআই থেকে রিপ্লাই আনা
    with st.chat_message("assistant"):
        with st.spinner("AI is thinking..."):
            response = requests.post(f"{API_BASE_URL}/get-reply/", json={"comment": user_comment})
            if response.status_code == 200:
                data = response.json()
                reply = data["ai_reply"]
                v_type = data.get("video_type", "Unknown")
                
                full_response = f"**[{v_type} Mode]** \n\n {reply}"
                st.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            else:
                st.error("Failed to get reply from AI.")