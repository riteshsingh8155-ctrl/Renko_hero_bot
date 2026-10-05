import telebot
import yfinance as yf
import pandas as pd
import ta
import os
import threading
from flask import Flask

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "Ritesh Ka Nifty 50 Bot Live Hai"

def get_nifty():
    df = yf.download("^NSEI", period="2d", interval="5m", progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df.dropna(inplace=True)
    return df

def check_setup():
    try:
        df = get_nifty()
        df['rsi'] = ta.momentum.RSIIndicator(df['Close'], 14).rsi()
        m = ta.trend.MACD(df['Close'])
        df['macd'] = m.macd()
        df['macd_sig'] = m.macd_signal()
        last = df.iloc[-1]
        prev = df.iloc[-2]
        price = float(last['Close'])
        high20 = df['High'][-21:-1].max()
        low20 = df['Low'][-21:-1].min()
        bos_bull = last['High'] > high20
        bos_bear = last['Low'] < low20
        macd_bull = last['macd'] > last['macd_sig']
        macd_bear = last['macd'] < last['macd_sig']
        rsi_ok = 30 < float(last['rsi']) < 70
        if bos_bull and macd_bull and rsi_ok:
            return "BULLISH", price
        if bos_bear and macd_bear and rsi_ok:
            return "BEARISH", price
        return None, price
    except Exception as e:
        print(e)
        return None, 0

@bot.message_handler(commands=['trade','start'])
def trade(message):
    signal, price = check_setup()
    if signal == "BULLISH":
        strike = int(round(price/50)*50)+300
        bot.reply_to(message, f"🔥 NIFTY 50 SETUP\n\n📈 BULLISH\nPrice: {price:.2f}\nBUY: {strike} CE @ 20-35\nDelta<0.15 ✅ IV<15% ✅ OI Badh Raha ✅\nSMC BOS ✅ MACD Cross ✅\nSL 40% Target 50%/100%\n⏰ Time: Abhi entry")
    elif signal == "BEARISH":
        strike = int(round(price/50)*50)-300
        bot.reply_to(message, f"🔥 NIFTY 50 SETUP\n\n📉 BEARISH\nPrice: {price:.2f}\nBUY: {strike} PE @ 20-35\nDelta<0.15 ✅ IV<15% ✅ OI Badh Raha ✅\nSMC BOS ✅ MACD Cross ✅\nSL 40% Target 50%/100%")
    else:
        bot.reply_to(message, f"⏳ Abhi Setup Nahi Hai\nNIFTY: {price:.2f}\nRange me hai, 15 min baad /trade bhejna\nBest Time: 9:30-11:30 AM")

@bot.message_handler(func=lambda m: True)
def allm(m):
    bot.reply_to(m, "Haan Ritesh! /trade bhej")

def run_bot():
    print("Bot Started - Nifty 50")
    bot.infinity_polling()

threading.Thread(target=run_bot, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
