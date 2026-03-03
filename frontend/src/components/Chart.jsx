import { useEffect, useMemo, useRef } from "react"
import { createChart } from "lightweight-charts"

export default function Chart({ events }) {
  const chartContainerRef = useRef()
  const chartRef = useRef()
  const candleSeriesRef = useRef()
  const volumeSeriesRef = useRef()

  const icebergEvents = useMemo(
    () => events.filter((event) => event.type === "iceberg"),
    [events]
  )

  useEffect(() => {
    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: { color: "#020617" },
        textColor: "#cbd5e1",
      },
      grid: {
        vertLines: { color: "#1e293b" },
        horzLines: { color: "#1e293b" },
      },
      width: Math.max(window.innerWidth - 460, 900),
      height: 620,
      rightPriceScale: {
        borderColor: "#334155",
      },
      timeScale: {
        borderColor: "#334155",
      },
    })

    chartRef.current = chart

    candleSeriesRef.current = chart.addCandlestickSeries()
    volumeSeriesRef.current = chart.addHistogramSeries({
      priceFormat: { type: "volume" },
      priceScaleId: "",
      color: "#3b82f6",
    })

    const onResize = () => {
      chart.applyOptions({
        width: Math.max(window.innerWidth - 460, 900),
      })
    }

    window.addEventListener("resize", onResize)

    return () => {
      window.removeEventListener("resize", onResize)
      chart.remove()
    }
  }, [])

  useEffect(() => {
    const event = events[events.length - 1]

    if (!event || !volumeSeriesRef.current) return

    if (event.type === "true_volume") {
      volumeSeriesRef.current.update({
        time: Math.floor(Date.now() / 1000),
        value: Math.abs(event.delta),
        color: event.delta > 0 ? "#22c55e" : "#ef4444",
      })
    }
  }, [events])

  useEffect(() => {
    if (!candleSeriesRef.current) return

    candleSeriesRef.current.setMarkers(
      icebergEvents.slice(-80).map((event, index) => ({
        id: `${event.side}-${event.price}-${index}`,
        time: Math.floor(Date.now() / 1000) - (icebergEvents.length - index),
        position: event.side === "Bid" ? "belowBar" : "aboveBar",
        color: event.confidence === "high" ? "#facc15" : "#e2e8f0",
        shape: "circle",
        text: `${event.side} ${event.replenishments}x`,
      }))
    )
  }, [icebergEvents])

  return <div ref={chartContainerRef} />
}
