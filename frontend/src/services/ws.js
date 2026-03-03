let socket = null

export function connectWS(onMessage) {
  socket = new WebSocket("ws://127.0.0.1:8000/ws")

  socket.onopen = () => {
    console.log("WS connected")
  }

  socket.onmessage = (event) => {
    const data = JSON.parse(event.data)
    onMessage(data)
  }

  socket.onclose = () => {
    console.log("WS reconnecting...")
    setTimeout(() => connectWS(onMessage), 2000)
  }
}