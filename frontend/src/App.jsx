import { useEffect, useState } from "react"
import Chart from "./components/Chart"
import StatsPanel from "./components/StatsPanel"
import { connectWS } from "./services/ws"

export default function App() {

  const [events, setEvents] = useState([])

  useEffect(() => {
    connectWS((event) => {
      setEvents(prev => [...prev.slice(-200), event])
    })
  }, [])

  return (
    <div style={{ display: "flex" }}>
      <Chart events={events} />
      <StatsPanel />
    </div>
  )
}