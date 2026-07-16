import json

def handler(request):
    if request.method == "GET":
        return ("FnO Bot is running! ✅", 200, {"Content-Type": "text/plain"})
    return (json.dumps({"ok": True}), 200, {"Content-Type": "application/json"})
