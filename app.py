from flask import Flask, request, jsonify
import requests
from collections import deque
import json
from flask import Response, stream_with_context
from constants import OLLAMA_API_URL, MODEL_NAME, MAX_HISTORY_LENGTH, DEBUG_MODE


app = Flask(__name__)
app.debug = DEBUG_MODE

# For now it's like this, in the future this may be handled on a database
# in order to have more consistent and complex answers
conversation_history = deque(maxlen=MAX_HISTORY_LENGTH)


@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    prompt = data.get("prompt", "")

    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400

    # Append user message to conversation history
    conversation_history.append({"role": "user", "content": prompt})

    # Prepare the context (last 50 messages)
    context = "\n".join(
        [
            f"{msg['role'].capitalize()}: {msg['content']}"
            for msg in conversation_history
        ]
    )

    ollama_request = {
        "model": MODEL_NAME,
        "prompt": context,  # Pass conversation history
        "stream": True,  # Enable streaming
    }

    # Create a streaming generator function
    def generate():
        with requests.post(
            OLLAMA_API_URL, json=ollama_request, stream=True
        ) as response:
            if response.status_code != 200:
                yield json.dumps({"error": "Failed to communicate with Ollama"}) + "\n"
                return

            ai_response = ""
            for line in response.iter_lines():
                if line:
                    chunk = json.loads(line.decode("utf-8"))
                    token = chunk.get("response", "")
                    ai_response += token  # Append to AI response
                    yield token  # Stream token in real-time

            # Append AI response to conversation history
            conversation_history.append({"role": "assistant", "content": ai_response})

    return Response(stream_with_context(generate()), content_type="text/plain")


if __name__ == "__main__":
    # Run the Flask app on port 5000
    # and host 127.0.0.1 this will only be available locally
    app.run()
