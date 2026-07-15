from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/webhook", methods=["GET"])
def home():
    return "FnO Bot is running! v3", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    return jsonify({"ok": True})
