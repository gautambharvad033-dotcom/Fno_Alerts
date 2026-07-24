# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify
import requests
import datetime

app = Flask(__name__)

BOT_TOKEN = "8613392574:AAF83_86w1TGHdYuZF5ZXjwQPJQD8ss7fCM"

@app.route("/api/webhook", methods=["GET"])
def home():
    return "FnO Bot running!", 200

@app.route("/api/webhook", methods=["POST"])
def webhook():
    update = request.get_json(silent=True) or {}
    msg = update.get("message", {})
    text = msg.get("text", "").strip().lower()
    chat_id = msg.get("chat", {}).get("id")
    if chat_id and text == "/test":
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={"chat_id": chat_id, "text": "Bot working! Emojis: 📊✅🔴🟢"}
        )
    return jsonify({"ok": True})
