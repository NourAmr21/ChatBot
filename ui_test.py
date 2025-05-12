import os
import json
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
from langchain.chains import ConversationChain
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory

# Load environment variables
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI client
client = OpenAI(api_key=openai_api_key)

# Load scraped company context
SCRAPED_DATA_PATH = "C:/Users/LENOVO/Downloads/scraped_data.json"
with open(SCRAPED_DATA_PATH, "r", encoding="utf-8") as f:
    scraped = json.load(f)
company_context = " ".join(item["text"].replace("\n", " ").strip() for item in scraped)

MEMORY_FILE = "C:/Users/LENOVO/Downloads/ChatBot/memory.json"
def save_to_memory(post):
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            memory_data = json.load(f)
    else:
        memory_data = []
    memory_data.append(post)
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory_data, f, indent=2, ensure_ascii=False)

# LangChain setup
llm = ChatOpenAI(temperature=0.5, openai_api_key=openai_api_key)
memory = ConversationBufferMemory(return_messages=True)
conversation = ConversationChain(
    llm=llm,
    memory=memory,
    verbose=False
)

# Streamlit UI
st.set_page_config(page_title="🤖 34ML ChatBot", layout="centered")
st.title("🤖 34ML ChatBot")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "awaiting_approval" not in st.session_state:
    st.session_state.awaiting_approval = None

if "last_reply" not in st.session_state:
    st.session_state.last_reply = None

if "last_image_url" not in st.session_state:
    st.session_state.last_image_url = None

if "approval_phase" not in st.session_state:
    st.session_state.approval_phase = None

if "image_prompt" not in st.session_state:
    st.session_state.image_prompt = None

# Main chat input
user_input = st.chat_input("Ask something...", key="main_input")
if user_input:
    if st.session_state.awaiting_approval:
        st.session_state.awaiting_approval = None
        st.session_state.last_reply = None
        st.session_state.last_image_url = None
        st.session_state.approval_phase = None
        st.session_state.image_prompt = None

    system_prompt = f"""You are a helpful assistant for 34ML.
Use the following company background when writing content:
{company_context}
Never answer questions unrelated to the company. Respond conversationally."""

    conversation.memory.chat_memory.messages = [
        {"role": "system", "content": system_prompt},
        *conversation.memory.chat_memory.messages
    ]

    reply = conversation.predict(input=user_input)
    st.session_state.chat_history.append({"user": user_input, "bot": reply})

    is_content = any(w in user_input.lower() for w in ["post", "blog", "email", "write", "content"])
    if is_content:
        st.session_state.awaiting_approval = user_input
        st.session_state.last_reply = reply
        st.session_state.approval_phase = "image_choice"

# Display chat history
chat_container = st.container()
with chat_container:
    for i, entry in enumerate(st.session_state.chat_history):
        with st.chat_message("user"):
            st.markdown(entry['user'])
        with st.chat_message("assistant"):
            st.markdown(entry['bot'])
            if entry.get("image_url"):
                st.image(entry["image_url"], width=300)
                st.markdown(f"🔗 [View Image in New Tab]({entry['image_url']})")

# If awaiting approval, handle approval flow
if st.session_state.awaiting_approval:
    reply = st.session_state.last_reply
    user_input = st.session_state.awaiting_approval
    st.markdown("---")

    if st.session_state.approval_phase == "image_choice":
        st.markdown("### ✅ Approve this content? Type 'yes' to approve or 'edit' to modify.")
        approval_text = st.text_input("Type your decision:", key="approval_input")

        if approval_text.lower() == "yes":
            generate_image = st.selectbox("🖼️ Generate image?", ["No", "Yes", "Custom"], index=0, key="gen_option")

            if generate_image == "Yes":
                st.session_state.image_prompt = f"An illustrative image representing this content:\n{reply[:300]}"
                st.session_state.approval_phase = "generate"
                st.rerun()

            elif generate_image == "Custom":
                custom_prompt = st.text_input("🖌️ Enter custom image prompt:", key="custom_prompt")
                if custom_prompt:
                    st.session_state.image_prompt = custom_prompt
                    st.session_state.approval_phase = "generate"
                    st.rerun()

            else:
                st.session_state.image_prompt = None
                st.session_state.approval_phase = "generate"
                st.rerun()

        elif approval_text.lower() == "edit":
            st.session_state.approval_phase = "edit"
            st.rerun()

        elif approval_text:
            st.info("🗑️ Content not saved.")
            st.session_state.awaiting_approval = None
            st.session_state.approval_phase = None

    elif st.session_state.approval_phase == "edit":
        edited_text = st.text_area("✏️ Paste your edited version:", value=reply)
        if st.button("Save Edited Version"):
            save_to_memory({"prompt": user_input, "response": edited_text})
            st.success("✅ Edited content saved.")
            st.session_state.chat_history[-1]["bot"] = edited_text
            st.session_state.awaiting_approval = None
            st.session_state.approval_phase = None

    elif st.session_state.approval_phase == "generate":
        image_url = None
        if st.session_state.image_prompt:
            try:
                image_response = client.images.generate(
                    prompt=st.session_state.image_prompt,
                    model="dall-e-2",
                    n=1,
                    size="512x512"
                )
                image_url = image_response.data[0].url
                st.image(image_url, caption="Generated Image", width=300)
                st.markdown(f"🔗 [View Image in New Tab]({image_url})")
                st.session_state.last_image_url = image_url
            except Exception as e:
                st.error(f"❌ Image generation failed: {e}")

        save_to_memory({"prompt": user_input, "response": reply, "image_url": st.session_state.last_image_url})
        st.success("✅ Content saved.")
        st.session_state.chat_history[-1]["image_url"] = st.session_state.last_image_url
        st.session_state.awaiting_approval = None
        st.session_state.approval_phase = None
        st.session_state.image_prompt = None

# Styling
st.markdown("""
<style>
    .stTextInput>div>div>input {
        font-size: 16px;
    }
    .stTextArea>div>textarea {
        font-size: 16px;
    }
</style>
""", unsafe_allow_html=True)
