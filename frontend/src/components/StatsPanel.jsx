function StatCard({ label, value }) {
  return (
    <div
      style={{
        background: "#111827",
        border: "1px solid #1f2937",
        borderRadius: 10,
        padding: "10px 12px",
      }}
    >
      <div style={{ color: "#93c5fd", fontSize: 12 }}>{label}</div>
      <div style={{ color: "#f8fafc", fontWeight: 700, marginTop: 4 }}>{value}</div>
    </div>
  )
}

export default function StatsPanel({ stats, wsStatus, events }) {
  const latestSignals = events.filter((x) => x.type === "iceberg").slice(-12).reverse()

  return (
    <div
      style={{
        width: "420px",
        background: "#030712",
        color: "white",
        padding: "18px",
        display: "flex",
        flexDirection: "column",
        gap: "16px",
        borderLeft: "1px solid #1f2937",
      }}
    >
      <div>
        <h3 style={{ margin: 0 }}>Market Intel Radar</h3>
        <div style={{ color: "#93c5fd", marginTop: 6 }}>WS: {wsStatus}</div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }}>
        <StatCard label="Icebergs 24h" value={stats.total} />
        <StatCard label="Completion" value={`${stats.completion_rate.toFixed(1)}%`} />
        <StatCard label="Avg size" value={stats.avg_size.toFixed(2)} />
        <StatCard label="Avg duration" value={`${stats.avg_duration.toFixed(1)}s`} />
        <StatCard label="High confidence" value={`${stats.high_confidence_share.toFixed(1)}%`} />
        <StatCard label="Cancelled" value={stats.cancelled} />
      </div>

      <div>
        <h4 style={{ margin: "0 0 8px 0" }}>Top liquidity levels</h4>
        <div style={{ maxHeight: 180, overflow: "auto", fontSize: 13 }}>
          {(stats.top_levels || []).map((level) => (
            <div
              key={`${level.price}`}
              style={{ display: "flex", justifyContent: "space-between", padding: "4px 0" }}
            >
              <span>{level.price}</span>
              <span style={{ color: "#86efac" }}>{level.score}</span>
            </div>
          ))}
        </div>
      </div>

      <div>
        <h4 style={{ margin: "0 0 8px 0" }}>Recent iceberg signals</h4>
        <div style={{ maxHeight: 220, overflow: "auto", fontSize: 13 }}>
          {latestSignals.map((event, idx) => (
            <div
              key={`${event.side}-${event.price}-${idx}`}
              style={{
                marginBottom: 6,
                paddingBottom: 6,
                borderBottom: "1px solid #1f2937",
              }}
            >
              <div>
                {event.side} @ {event.price} • {event.confidence}
              </div>
              <div style={{ color: "#94a3b8" }}>
                replenishments: {event.replenishments} • duration: {event.duration?.toFixed?.(1) ?? 0}s
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
