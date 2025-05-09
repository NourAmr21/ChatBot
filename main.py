import openai 
import json
import os

openai.api_key = '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'
#######################################################################################
with open(r"C:\Users\LENOVO\Downloads\scraped_data.json", "r", encoding="utf-8") as f:
    scraped = json.load(f)
company_context = scraped[0]["text"].replace("\n", " ").strip()[:3000]
def save_memory():
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=2, ensure_ascii=False)

# Load memory
MEMORY_FILE = "memory.json"
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
        response = openai.ChatCompletion.create(
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
