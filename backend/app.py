from flask_cors import CORS
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)
CORS(app)

# 🗄️ Simple database (basic)
def check_database(user_input):
    data = {
        "dbms": "DBMS is a system used to manage databases efficiently.",
        "os": "Operating System manages hardware and software.",
        "gd tips": "Speak clearly, be confident, and listen actively."
    }

    user_input = user_input.lower()

    for key in data:
        if key in user_input:
            return data[key]

    return None

# 🤖 OpenRouter AI function
def get_ai_response(user_input):
    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": "Bearer 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",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost",
        "X-Title": "chatbot"
    }

    data = {
        "model": "meta-llama/llama-3-8b-instruct",
        "messages": [
            {"role": "user", "content": f"You are an interview preparation assistant. Answer clearly in well-structured paragraphs with proper spacing. Do not shorten the answer. Avoid a single long paragraph and make it easy to read: {user_input}"}
        ]
    }

    response = requests.post(url, headers=headers, json=data)
    result = response.json()

    # ✅ SAFE handling
    if "choices" in result:
        return result["choices"][0]["message"]["content"]
    else:
        return "Error from AI: " + str(result)

# 🤖 Chat endpoint
@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message")

    if not user_input:
        return jsonify({"reply": "Please enter a valid question."})

    # Step 1: Check database
    db_response = check_database(user_input)

    if db_response:
        return jsonify({"reply": db_response})

    # Step 2: OpenRouter AI
    reply = get_ai_response(user_input)

    return jsonify({"reply": reply})


if __name__ == "__main__":
    app.run(debug=True, port=5002)