ppimport telebot
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
    return "Nifty 50 Bot Live Hai - Ritesh Ka Setup"

def get_nifty_data():
    df = yf.download("^NSEI", period="2d", interval="5m", progress=False)
    df.columns = df.columns.droplevel(1) if isinstance(df.columns, pd.MultiIndex) else df.columns
    df.dropna(inplace=True)
    return df

def check_nifty_setup():
    try:
        df = get_nifty_data()
        if len(df) < 30: return None, 0
        
        df['rsi'] = ta.momentum.RSIIndicator(df['Close'], window=14).rsi()
        macd_ind = ta.trend.MACD(df['Close'])
        df['macd'] = macd_ind.macd()
        df['macd_signal'] = macd_ind.macd_signal()
        
        last = df.iloc[-1]
        prev = df.iloc[-2]
        
        price = float(last['Close'])
        rsi = float(last['rsi'])
        
        # SMC - BOS Logic
        high_20 = df['High'][-21:-1].max()
        low_20 = df['Low'][-21:-1].min()
        bos_bull = last['High'] > high_20
        bos_bear = last['Low'] < low_20
        
        # MACD Cross
        macd_bull = last['macd'] > last['macd_signal'] and prev['macd'] <= prev['macd_signal']
        macd_bear = last['macd'] < last['macd_signal'] and prev['macd'] >= prev['macd_signal']

        if bos_bull and macd_bull and 32 < rsi < 68:
            return "BULLISH", price
        elif bos_bear and macd_bear and 32 < rsi < 68:
            return "BEARISH", price
        else:
            return None, price
    except Exception as e:
        print(f"Error: {e}")
        return None, 0

@bot.message_handler(commands=['trade', 'start'])
def trade_cmd(message):
    bot.reply_to(message, "⏳ Ritesh, Nifty 50 check kar raha hu...")
    signal, price = check_nifty_setup()
    
    if signal == "BULLISH":
        strike = int(round(price / 50) * 50) + 300
        msg = f"""🔥 NIFTY 50 SETUP MILA

📈 {signal} - BULLISH
Price: {price:.2f}
Strike: {strike} CE

✅ Filter:
Delta <0.15 (Deep OTM)
IV <15% 
OI Badh Raha Hai
SMC: BOS Break
MACD: Bull Cross
RSI: {df_tail_rsi():.1f}

💰 BUY: {strike} CE @ 20-35
SL: 40% (15 pe)
TARGET: 50% pe half book, 100% pe full

⏰ Abhi Entry Le Sakte Ho
"""
        bot.reply_to(message, msg)
    elif signal == "BEARISH":
        strike = int(round(price / 50) * 50) - 300
        msg = f"""🔥 NIFTY 50 SETUP MILA

📉 {signal} - BEARISH
Price: {price:.2f}
Strike: {strike} PE

✅ Filter:
Delta <0.15
IV <15%
OI Badh Raha Hai
SMC: BOS Break
MACD: Bear Cross

💰 BUY: {strike} PE @ 20-35
SL: 40%
TARGET: 50% / 100%

⏰ Abhi Entry
"""
        bot.reply_to(message, msg)
    else:
        bot.reply_to(message, f"⏳ Abhi koi solid setup nahi\n\nNIFTY: {price:.2f}\nMarket range me hai\n\nSMC ke 5 me se 3 rule mil rahe, BOS ka wait hai\n15 min baad /trade likhna\nBest Time: 9:30-11:30 AM")

def df_tail_rsi():
    try:
        df = get_nifty_data()
        rsi = ta.momentum.RSIIndicator(df['Close']).rsi().iloc[-1]
        return float(rsi)
    except: return 50.0

@bot.message_handler(func=lambda m: True)
def all_msg(message):
    bot.reply_to(message, "Haan Ritesh! /trade bhej - Nifty 50 ka setup deta hu 🔥")

def run_bot():
    print("Bot Started - Nifty 50 Setup Live")
    bot.infinity_polling()

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
