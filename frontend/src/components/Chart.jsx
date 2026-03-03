import { useEffect, useRef } from "react"
import { createChart } from "lightweight-charts"

export default function Chart({ events }) {
  const chartContainerRef = useRef()
  const chartRef = useRef()
  const candleSeriesRef = useRef()
  const volumeSeriesRef = useRef()

  useEffect(() => {
    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: { color: "#0f172a" },
        textColor: "#d1d5db"
      },
      grid: {
        vertLines: { color: "#1e293b" },
        horzLines: { color: "#1e293b" }
      },
      width: window.innerWidth - 300,
      height: 600
    })

    chartRef.current = chart

    candleSeriesRef.current = chart.addCandlestickSeries()
    volumeSeriesRef.current = chart.addHistogramSeries({
      priceFormat: { type: "volume" },
      priceScaleId: ""
    })

    return () => chart.remove()
  }, [])

  useEffect(() => {
    events.forEach(event => {

      if (event.type === "iceberg") {
        candleSeriesRef.current.setMarkers([
          {
            time: Math.floor(Date.now() / 1000),
            position: event.side === "Bid" ? "belowBar" : "aboveBar",
            color: event.confidence === "high" ? "yellow" : "white",
            shape: "circle",
            text: `${event.side} ${event.replenishments}`
          }
        ])
      }

      if (event.type === "true_volume") {
        volumeSeriesRef.current.update({
          time: Math.floor(Date.now() / 1000),
          value: Math.abs(event.delta),
          color: event.delta > 0 ? "#16a34a" : "#dc2626"
        })
      }

    })
  }, [events])

  return <div ref={chartContainerRef} />
}