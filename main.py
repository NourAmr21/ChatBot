import openai 
import json
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI()
#######################################################################################
with open(r"C:\Users\LENOVO\Downloads\scraped_data.json", "r", encoding="utf-8") as f:
    scraped = json.load(f)
#company_context = scraped[0]["text"].replace("\n", " ").strip()[:3000]
company_context = ""
for item in scraped:
    company_context += item["text"].replace("\n", " ").strip()[:] + " " 
MEMORY_FILE = r"C:\Users\LENOVO\Downloads\ChatBot\memory.json"
def save_memory():
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=2, ensure_ascii=False)

# Load memory

if os.path.exists(MEMORY_FILE):
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        memory = json.load(f)
else:
    memory = []

def is_duplicate(new_post):
    return any(new_post.strip() in old.strip() for old in memory)

def add_to_memory(post):
    memory.append(post)
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=2, ensure_ascii=False)



def generate_reply(user_input):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": f"""You are a helpful assistant for 34ML.
If the user asks you to generate content (such as blog posts, LinkedIn posts, or email campaigns), use the following company background to guide tone and style:
\"\"\"
{company_context}
\"\"\"
Otherwise, respond conversationally and helpfully. For example, greet the user back but never answer questions unrelated to the company.
 You are not supposed to use any other information from the internet.
   You are strictly a bot for comapny content."""
                },
                {"role": "user", "content": user_input}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ Error: {e}"

###########################################################################################
if __name__ == "__main__":
    print("🤖 34BOT is ready. Type a prompt or 'exit' to quit.")

    while True:
        user_input = input("\nYou: ").strip()
        if user_input.lower() in ["exit", "quit", "bye"]:
            break
        if not user_input:
            print("⚠️ Please enter a message.")
            continue

        response = generate_reply(user_input)
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
                        #record["image_url"] = image_url
                    except Exception as e:
                        print(f"❌ Failed to generate image: {e}")
                memory.append(response)
                save_memory()
                print("✅ Saved to memory.")
            elif approval == "edit":
                edited = input("✏️ Paste your edited version: ").strip()
                memory.append(edited)
                save_memory()
                print("✅ Edited version saved.")
            else:
                print("🗑️ Not saved.")
