import { useEffect, useMemo, useState } from "react"
import Chart from "./components/Chart"
import StatsPanel from "./components/StatsPanel"
import { connectWS } from "./services/ws"

const defaultStats = {
  total: 0,
  completed: 0,
  cancelled: 0,
  completion_rate: 0,
  avg_size: 0,
  avg_duration: 0,
  high_confidence_share: 0,
  top_levels: [],
}

export default function App() {
  const [events, setEvents] = useState([])
  const [stats, setStats] = useState(defaultStats)
  const [wsStatus, setWsStatus] = useState("connecting")

  useEffect(() => {
    const disconnect = connectWS({
      onMessage: (event) => setEvents((prev) => [...prev.slice(-600), event]),
      onStatusChange: setWsStatus,
    })

    return disconnect
  }, [])

  useEffect(() => {
    let timer

    const loadStats = async () => {
      try {
        const response = await fetch("http://127.0.0.1:8000/dashboard")
        const data = await response.json()
        setStats({ ...defaultStats, ...data })
      } catch (error) {
        console.error("Stats fetch failed", error)
      }
    }

    loadStats()
    timer = setInterval(loadStats, 4000)

    return () => clearInterval(timer)
  }, [])

  const title = useMemo(() => {
    const lastVolume = [...events].reverse().find((item) => item.type === "true_volume")

    if (!lastVolume) return "No large prints yet"

    const side = lastVolume.delta > 0 ? "Buy pressure" : "Sell pressure"
    return `${side}: ${Math.abs(lastVolume.delta).toFixed(2)}`
  }, [events])

  return (
    <div style={{ display: "flex", background: "#020617", minHeight: "100vh" }}>
      <div style={{ padding: 16, flex: 1 }}>
        <h1 style={{ color: "#f8fafc", marginTop: 0 }}>Iceberg Vision Pro</h1>
        <div style={{ color: "#93c5fd", marginBottom: 12 }}>{title}</div>
        <Chart events={events} />
      </div>
      <StatsPanel stats={stats} wsStatus={wsStatus} events={events} />
    </div>
  )
}
