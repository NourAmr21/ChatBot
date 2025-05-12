# 🤖 34ML Company Chatbot

A conversational AI assistant built using **Streamlit**, **LangChain**, and **OpenAI**, designed to interact with users based on scraped company context and generate high-quality content such as posts or emails with optional image generation via DALL·E.

## 🚀 Features

- **Conversational Chatbot** with memory using LangChain
- Loads and uses scraped company data for responses
- Detects post/content requests and prompts for approval
- Offers content editing before saving
- Optionally generates images for content using DALL·E
- Saves approved content (text + image URL) to a local memory file
- Clean Streamlit UI with persistent session state (some issues with re-rendering to be fixed)
- Currently, the CLI bot supports all funcionalities.

## 📂 Project Structure

├── 34BOT_lang.py # CLI BOT
├── ui_test.py # Main Streamlit app
├── memory.json # Local memory of saved content
├── scraped_data.json # JSON file with company context
├── scraper.py # Python script for scraping the website using BeautifulSoup (can be used to schedule periodic scraping to update the context of the bot as the website gets updated)
├── .env # Environment variables (e.g. OpenAI API key)
└── README.md # Project documentation


## 🔧 Requirements

- Python 3.9+
- `streamlit`
- `openai`
- `langchain`
- `python-dotenv`

- Install all dependencies using:

- <pre> pip install -r requirements.txt </pre>

- Create a .env file with your OpenAI key:
- OPENAI_API_KEY=your_openai_key_here

## 🧠 How It Works
- User submits a prompt via the chat input.

- LangChain + OpenAI processes it with memory and scraped context.

- If the prompt is a content-type request (e.g. post, blog, email), the bot enters an approval workflow:

- User reviews the generated content.

- Optionally edits the content.

- Optionally generates an image (default, custom, or skip).

- Final output is saved to memory.json.

## 🖼️ Image Generation
- Uses DALL·E via OpenAI's API.

- Triggered only if user explicitly approves content and chooses image generation.

- Image URL is shown in the chat interface.

## 💾 Content Persistence
- Approved content is saved to a JSON file with:

- {
-  "prompt": "write a post about AI",
-  "response": "Here is a thoughtful AI post...",
-  "image_url": "https://image.url"
- }

## 📌 Notes
- This chatbot is domain-aware and refuses to answer off-topic prompts.

- State is managed using st.session_state to preserve memory, history, and approval flow.
