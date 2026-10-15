from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)

def run_chat_loop():
    messages = [
        {
            "role": "system",
            "content": "You are an academic mentor. Keep track of everything the user tells you."
        }
    ]

    while True:
        user_input = input("User: ")

        if user_input.strip().lower() in ("exit", "quit"):
            break

        messages.append({"role": "user", "content": user_input})

        response = client.chat.completions.create(
            model="qwen2.5:1.5b",
            temperature=0.2,
            messages=messages
        )

        assistant_reply = response.choices[0].message.content

        print(f"Assistant: {assistant_reply}")

        messages.append({"role": "assistant", "content": assistant_reply})

if __name__ == "__main__":
    run_chat_loop()