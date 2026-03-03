import { useEffect, useState } from "react"

export default function StatsPanel() {

  const [stats, setStats] = useState(null)

  useEffect(() => {
    fetch("http://127.0.0.1:8000/stats")
      .then(res => res.json())
      .then(data => setStats(data))
  }, [])

  if (!stats) return <div>Loading...</div>

  return (
    <div style={{
      width: "280px",
      background: "#111827",
      color: "white",
      padding: "20px"
    }}>
      <h3>АЙСБЕРГИ 24ч</h3>
      <p>Всего: {stats.total}</p>
      <p>Исполнено: {stats.completed}</p>
      <p>Отменено: {stats.cancelled}</p>
      <p>Completion: {stats.completion_rate.toFixed(1)}%</p>
      <p>Средний объем: {stats.avg_size.toFixed(2)}</p>
      <p>Средняя длительность: {stats.avg_duration.toFixed(1)}с</p>
    </div>
  )
}