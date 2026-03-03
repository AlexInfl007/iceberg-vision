let socket = null
let reconnectTimer = null

export function connectWS({ onMessage, onStatusChange }) {
  const connect = () => {
    onStatusChange?.("connecting")
    socket = new WebSocket("ws://127.0.0.1:8000/ws")

    socket.onopen = () => {
      onStatusChange?.("connected")
    }

    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        onMessage?.(data)
      } catch (error) {
        console.error("WS parse error", error)
      }
    }

    socket.onerror = () => {
      onStatusChange?.("error")
    }

    socket.onclose = () => {
      onStatusChange?.("reconnecting")
      reconnectTimer = setTimeout(connect, 2000)
    }
  }

  connect()

  return () => {
    if (reconnectTimer) {
      clearTimeout(reconnectTimer)
    }

    if (socket && socket.readyState <= 1) {
      socket.close()
    }
  }
}
