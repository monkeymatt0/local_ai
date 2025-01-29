import requests
import json
from collections import deque

OLLAMA_API_URL = "http://localhost:11434/api/generate"  # Default Ollama API URL
MODEL_NAME = "deepseek-r1:8b"  # Use the model you pulled in Ollama


# Initialize a deque to hold conversation history with a maximum length of 50 messages
MAX_HISTORY_LENGTH = 50
conversation_history = deque(maxlen=MAX_HISTORY_LENGTH)


def generate_response(prompt):
    # Append the new user message to the conversation history
    conversation_history.append({"role": "user", "content": prompt})

    # Prepare the context by including past messages (up to the last 50)
    context = "\n".join(
        [
            f"{msg['role'].capitalize()}: {msg['content']}"
            for msg in conversation_history
        ]
    )

    payload = {
        "model": MODEL_NAME,
        "prompt": context,  # Pass conversation history
        "stream": True,
    }

    response = requests.post(OLLAMA_API_URL, json=payload, stream=True)

    if response.status_code == 200:
        print("\nAI Response:", end=" ")
        ai_response = ""
        for line in response.iter_lines():
            if line:
                chunk = json.loads(line.decode("utf-8"))
                ai_response += chunk["response"]
                print(chunk["response"], end="", flush=True)  # Print in real-time

        # Append AI response to history
        conversation_history.append({"role": "assistant", "content": ai_response})
    else:
        print(f"Error: {response.status_code}, {response.text}")


if __name__ == "__main__":
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        generate_response(user_input)
