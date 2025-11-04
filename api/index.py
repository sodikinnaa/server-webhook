from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import os, json
from pathlib import Path
from services.WhatsappSender import WhatsappSender

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# wzs_api = wzs_api()
# output = wzs_api.send_message("6288275426716", "Hello, this is a test message")
# print(json.dumps(output, indent=4))
PORT_SERVER=os.getenv('PORT_SERVER')
app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/webhook", methods=["POST"])
def webhook():
    wzs_api = WhatsappSender()
    data = request.json
    chat = ''
    phone = ''
    # Safely access nested data to avoid AttributeError if any key is missing or None
    event = data.get("event") if data else None
    sender = event.get("Info", {}).get("Sender") if event else None
    conversation = event.get("Message", {}).get("conversation") if event else None
    isForMe = event.get("Info", {}).get("IsFromMe") if event else None
    if conversation:
        chat = conversation
        string_chat = chat.lower()
        # Extract the number from sender like "6288275426716:79@s.whatsapp.net"
        if sender and isinstance(sender, str):
            phone = sender.split(':')[0] if ':' in sender else sender
            message = wzs_api.message_to_reply(string_chat, chat, phone)
            wzs_api.send_message("6288275426716",message)

    if chat:
        print("kore wa data : " + chat + " from : " + phone )
    else:
        print("Tidak Menerima Pesan ")
    return jsonify({"message": "Webhook received"}), 200

if __name__ == "__main__":
    app.run(debug=True, port=PORT_SERVER, host="0.0.0.0", use_reloader=True)