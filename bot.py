import telebot, yfinance as yf, pandas as pd, ta, os, threading
from flask import Flask

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "Nifty 50 Bot Live"

def get_nifty():
    df = yf.download("^NSEI", period="2d", interval="5m", progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df.dropna(inplace=True)
    return df

@bot.message_handler(commands=['trade','start'])
def trade(m):
    bot.reply_to(m, "⏳ Nifty 50 check kar raha hu Ritesh...")
    try:
        df = get_nifty()
        df['rsi'] = ta.momentum.RSIIndicator(df['Close'],14).rsi()
        macd = ta.trend.MACD(df['Close'])
        df['macd'] = macd.macd()
        df['macd_s'] = macd.macd_signal()
        last = df.iloc[-1]
        price = float(last['Close'])
        high20 = df['High'][-21:-1].max()
        low20 = df['Low'][-21:-1].min()
        
        bull = last['High'] > high20 and last['macd'] > last['macd_s']
        bear = last['Low'] < low20 and last['macd'] < last['macd_s']
        
        if bull:
            strike = int(round(price/50)*50)+300
            bot.reply_to(m, f"🔥 NIFTY BULLISH\nPrice: {price:.2f}\nBUY {strike} CE @ 25-35\nDelta<0.15 IV<15% BOS Break\nSL 40% TG 50%/100%")
        elif bear:
            strike = int(round(price/50)*50)-300
            bot.reply_to(m, f"🔥 NIFTY BEARISH\nPrice: {price:.2f}\nBUY {strike} PE @ 25-35\nDelta<0.15 IV<15% BOS Break\nSL 40% TG 50%/100%")
        else:
            bot.reply_to(m, f"⏳ No Setup Abhi\nNIFTY: {price:.2f} Range me hai\n15 min baad /trade bhejna\nBest: 9:30-11:30 AM")
    except Exception as e:
        bot.reply_to(m, f"Error: {e}")

@bot.message_handler(func=lambda x: True)
def any_msg(m):
    bot.reply_to(m, "Haan Ritesh! /trade bhej")

def run_bot():
    print("Bot Started")
    bot.infinity_polling()

threading.Thread(target=run_bot, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
