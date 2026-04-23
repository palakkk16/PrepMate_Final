from flask_cors import CORS
from flask import Flask, request, jsonify
import requests
import uuid

app = Flask(__name__)
CORS(app)

# Store chats
chats = {}

# 🤖 AI function
def get_ai_response(chat_history):
    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": "Bearer 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",  # 👈 PUT YOUR KEY HERE
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost",
        "X-Title": "PrepMate"
    }

    messages = [
        {
            "role": "system",
            "content": (
                "You are an interview preparation assistant. "
                "Always maintain context of conversation. "
                "If user asks follow-up questions like 'give example', "
                "you must relate it to previous topic. "
                "Give clear and structured answers."
            )
        }
    ] + chat_history

    data = {
        "model": "openai/gpt-3.5-turbo",  # ✅ better for context
        "messages": messages
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        result = response.json()
        print(result)

        if "choices" in result:
            return result["choices"][0]["message"]["content"]
        else:
            return "AI Error: " + str(result)

    except Exception as e:
        print(e)
        return "Connection Error"


# 🤖 Chat route
@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_input = data.get("message")
    chat_id = data.get("chat_id")

    if not user_input:
        return jsonify({"reply": "Please enter a valid question."})
    
    vague_inputs = ["example", "real life example", "give example", "its", "it", "that", "why"]

    if any(phrase in user_input.lower() for phrase in vague_inputs):
        # check if previous user message exists
        has_previous_user = any(
            msg["role"] == "user" for msg in chats.get(chat_id, [])
        )

        # only block if NO previous context
        if not has_previous_user:
            return jsonify({
                "reply": "Please specify the topic. For example: 'Give real-life example of OOP'"
            })

    # Create new chat
    if not chat_id:
        chat_id = str(uuid.uuid4())
        chats[chat_id] = []

    if chat_id not in chats:
        chats[chat_id] = []

    # 🔥 Handle vague follow-ups safely
    ambiguous_phrases = ["example", "real life example", "give example", "explain more", "why", "its", "it", "that"]

    if any(phrase in user_input.lower() for phrase in ambiguous_phrases):
        last_user = None

        if len(chats[chat_id]) > 0:
            for msg in reversed(chats[chat_id]):
                if msg["role"] == "user":
                    last_user = msg["content"]
                    break

        if last_user:
            user_input = f"{user_input} (related to: {last_user})"

    # Save user message
    chats[chat_id].append({
        "role": "user",
        "content": user_input
    })

    # Get AI response
    reply = get_ai_response(chats[chat_id])

    # Save bot reply
    chats[chat_id].append({
        "role": "assistant",
        "content": reply
    })

    return jsonify({
        "reply": reply,
        "chat_id": chat_id
    })


if __name__ == "__main__":
    app.run(debug=True, port=5002)