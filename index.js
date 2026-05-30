const express = require('express');
const WebSocket = require('ws');
const { RSI } = require('technicalindicators');
const protobuf = require('protobufjs');
const axios = require('axios');

const app = express();
const PORT = process.env.PORT || 3000;
app.get('/', (req, res) => res.send('ATM RSI Scanner Running'));
app.listen(PORT, () => {
  console.log(`Server ${PORT} pe start`);
  startScanner();
});

const CONFIG = {
  UNDERLYING: "NSE_INDEX|Nifty 50", // "NSE_FO|RELIANCE" jaise future stock daal de
  EXPIRY: "28SEP2024", // Weekly expiry DDMMMYYYY format. Auto detect karna ho to code neeche hai
  RSI_PERIOD: 14,
  RSI_THRESHOLD: 60,
  STRIKE_STEP: 50, // Nifty 50, BankNifty 100, Stocks alag
  TELEGRAM_TOKEN: process.env.TELEGRAM_TOKEN,
  TELEGRAM_CHAT_ID: process.env.TELEGRAM_CHAT_ID
};

const strikeData = {};
let MarketDataFeed = null;
let currentATM_CE = null;
let currentATM_PE = null;
let underlyingLTP = 0;

protobuf.load("MarketDataFeed.proto").then(root => {
  MarketDataFeed = root.lookupType("MarketDataFeed");
  console.log("Protobuf loaded");
});

function startScanner() {
  const ws = new WebSocket(
    `wss://wsfeeder-api.upstox.com/market-data-feeder/v2/upstox-developer-api/feeder`,
    {
      headers: {
        "Authorization": `Bearer ${process.env.UPSTOX_ACCESS_TOKEN}`,
        "Api-Version": "2.0"
      }
    }
  );

  ws.on('open', () => {
    console.log('Connected to Upstox');

    // Pehle underlying ka LTP le ATM nikalne ke liye
    const subUnderlying = {
      guid: "underlying-1",
      method: "sub",
      data: { mode: "ltpc", instrumentKeys: [CONFIG.UNDERLYING] }
    };
    ws.send(Buffer.from(JSON.stringify(subUnderlying)));
  });

  ws.on('message', async (data) => {
    if (!MarketDataFeed) return;

    try {
      const decoded = MarketDataFeed.decode(data);
      const jsonData = MarketDataFeed.toObject(decoded);

      if (jsonData.feeds) {
        for (let key in jsonData.feeds) {
          const feed = jsonData.feeds[key];

          // 1. Underlying ka LTP update karo
          if (key === CONFIG.UNDERLYING && feed.ltpc) {
            underlyingLTP = feed.ltpc.ltp;

            // ATM strike calculate karo
            const atmStrike = Math.round(underlyingLTP / CONFIG.STRIKE_STEP) * CONFIG.STRIKE_STEP;
            const atmCE = `NSE_FO|${CONFIG.UNDERLYING.split('|')[1]}${CONFIG.EXPIRY}${atmStrike}CE`;
            const atmPE = `NSE_FO|${CONFIG.UNDERLYING.split('|')[1]}${CONFIG.EXPIRY}${atmStrike}PE`;

            // Agar ATM change hua to naya subscribe karo
            if (atmCE!== currentATM_CE) {
              console.log(`New ATM: ${atmStrike}. Subscribing ${atmCE} & ${atmPE}`);
              currentATM_CE = atmCE;
              currentATM_PE = atmPE;

              const subATM = {
                guid: "atm-sub",
                method: "sub",
                data: { mode: "full", instrumentKeys: [atmCE, atmPE] }
              };
              ws.send(Buffer.from(JSON.stringify(subATM)));
            }
          }

          // 2. ATM strikes ka data process karo
          if (feed.fullFeed && feed.fullFeed.marketFF) {
            const ltp = feed.fullFeed.marketFF.ltpc.ltp;
            processStrike(key, ltp, underlyingLTP);
          }
        }
      }
    } catch (e) {
      console.error("Decode error:", e.message);
    }
  });

  ws.on('close', () => setTimeout(startScanner, 5000));
}

function processStrike(instrumentKey, ltp, spot) {
  if (!strikeData[instrumentKey]) {
    strikeData[instrumentKey] = { prices: [], lastRsi: 0 };
  }

  const strike = strikeData[instrumentKey];
  strike.prices.push(ltp);

  if (strike.prices.length > CONFIG.RSI_PERIOD + 1) {
    strike.prices.shift();

    const rsiValues = RSI.calculate({
      values: strike.prices,
      period: CONFIG.RSI_PERIOD
    });

    const currentRsi = rsiValues[rsiValues.length - 1];
    const strikeName = instrumentKey.split('|')[1];

    // RSI 60 cross up
    if (strike.lastRsi < CONFIG.RSI_THRESHOLD && currentRsi >= CONFIG.RSI_THRESHOLD) {
      const msg = `🚨 ATM RSI ALERT\n${strikeName}\nSpot: ${spot}\nLTP: ${ltp}\nRSI 14: ${currentRsi.toFixed(2)} Crossed 60 UP`;
      console.log(msg);
      sendTelegram(msg);
    }

    strike.lastRsi = currentRsi;
  }
}

async function sendTelegram(message) {
  if (!CONFIG.TELEGRAM_TOKEN ||!CONFIG.TELEGRAM_CHAT_ID) return;
  try {
    await axios.post(`https://api.telegram.org/bot${CONFIG.TELEGRAM_TOKEN}/sendMessage`, {
      chat_id: CONFIG.TELEGRAM_CHAT_ID,
      text: message
    });
  } catch (e) {
    console.error("Telegram error:", e.message);
  }
}
