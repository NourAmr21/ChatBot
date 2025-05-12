import os
import json
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from openai import OpenAI

# Load environment variables
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)

# Load scraped company data
SCRAPED_FILE = r"C:\Users\LENOVO\Downloads\scraped_data.json"
with open(SCRAPED_FILE, "r", encoding="utf-8") as f:
    scraped = json.load(f)

company_context = " ".join(item["text"].replace("\n", " ").strip() for item in scraped)

# Load or initialize memory
MEMORY_FILE = r"C:\Users\LENOVO\Downloads\ChatBot\memory.json"
if os.path.exists(MEMORY_FILE):
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        memory_log = json.load(f)
else:
    memory_log = []

def save_memory():
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory_log, f, indent=2, ensure_ascii=False)

# LangChain memory & prompt setup
memory = ConversationBufferMemory()
prompt = PromptTemplate(
    input_variables=["history", "input"],
    template=(
        "You are a helpful assistant for 34ML.\n"
        "If the user asks you to generate content (e.g., blog posts, LinkedIn posts, or emails), "
        "use the following company background for tone and style:\n"
        "\"\"\"\n{company_context}\n\"\"\"\n"
        "Otherwise, respond conversationally and helpfully. Never answer questions unrelated to the company.\n\n"
        "Chat history:\n{history}\nUser: {input}\nAI:"
    )
)

llm = ChatOpenAI(
    openai_api_key=openai_api_key,
    model_name="gpt-3.5-turbo",
    temperature=0.7
)

chain = ConversationChain(
    llm=llm,
    memory=memory,
    prompt=prompt.partial(company_context=company_context),
    verbose=False
)

# Chat loop
if __name__ == "__main__":
    print("🤖 34BOT with LangChain memory is ready. Type 'exit' to quit.")

    while True:
        user_input = input("\nYou: ").strip()
        if user_input.lower() in ["exit", "quit", "bye"]:
            break
        if not user_input:
            print("⚠️ Please enter a message.")
            continue

        response = chain.predict(input=user_input)
        print("\n34BOT:", response)

        # Trigger approval only if it's likely a generated piece of content
        looks_like_content = (
            len(response.split()) > 30 and
            any(word in user_input.lower() for word in ["post", "blog", "email", "write", "content"])
        )

        if looks_like_content:
            approval = input("\n✅ Approve this content? (yes/no/edit): ").strip().lower()
            if approval == "yes":
                generate_image = input("🖼️ Generate an image for this post? (yes/no/custom): ").strip().lower()
                if generate_image in ["yes", "custom"]:
                    if generate_image == "yes":
                        image_prompt = f"An illustrative image that visually represents the following content:\n{response[:300]}"
                    else:
                        image_prompt = input("🖌️ Enter your custom image prompt: ").strip()

                    try:
                        img_response = client.images.generate(
                            model="dall-e-3",
                            prompt=image_prompt,
                            n=1,
                            size="1024x1024"
                        )
                        image_url = img_response.data[0].url
                        print(f"📷 Image generated: {image_url}")
                    except Exception as e:
                        print(f"❌ Failed to generate image: {e}")
                memory_log.append(response)
                save_memory()
                print("✅ Saved to memory.")
            elif approval == "edit":
                edited = input("✏️ Paste your edited version: ").strip()
                memory_log.append(edited)
                save_memory()
                print("✅ Edited version saved.")
            else:
                print("🗑️ Not saved.")
