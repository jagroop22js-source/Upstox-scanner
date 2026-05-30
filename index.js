const ws = new WebSocket('wss://api.upstox.com/v2/feed', {
  family: 4  // ye line add kar de - IPv4 force karega
});
