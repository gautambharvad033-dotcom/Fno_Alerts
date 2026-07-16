from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/api/webhook", methods=["GET"])
def home():
    return "FnO Bot is running! ✅", 200

@app.route("/api/webhook", methods=["POST"])
def webhook():
    return jsonify({"ok": True})
