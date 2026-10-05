import requests, time, threading
from flask import Flask
BOT_TOKEN = "8871619012:AAHtaAwMPGYkho1eUX5Vnc-i9JLcR8I8hrw"
API = f"https://api.telegram.org/bot{BOT_TOKEN}"
app = Flask(__name__)
@app.route('/')
def home():
    return "Devil Bot Running 24x7 🔥"
def bot_loop():
    last_id = 0
    while True:
        try:
            r = requests.get(f"{API}/getUpdates", params={"offset": last_id+1, "timeout":10}).json()
            for u in r.get("result", []):
                last_id = u["update_id"]
                if "message" not in u: continue
                chat_id = u["message"]["chat"]["id"]
                text = u["message"].get("text","").lower()
                if "/trade" in text or "trade" in text:
                    reply = "🔥 DEVIL RENKO SETUP 🔥\n\nBANKNIFTY BUY 54300\nSL 54100\nTARGET 54700\n\nRitesh sun setup ban raha hai! 🚀"
                else:
                    reply = "Haan bol Ritesh! /trade bhej"
                requests.get(f"{API}/sendMessage", params={"chat_id": chat_id, "text": reply})
        except:
            time.sleep(2)
threading.Thread(target=bot_loop, daemon=True).start()
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
