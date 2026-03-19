import * as d3 from "d3"
import { useEffect, useRef } from "react"
import type { HistogramBucket } from "../../types/common"

interface Props {
  data: HistogramBucket[]
  height?: number
}

export default function HistogramChart({ data, height: h = 160 }: Props) {
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!ref.current) return
    const container = ref.current
    container.innerHTML = ""

    if (data.length === 0) return

    const width = container.clientWidth
    const height = h
    const margin = { top: 10, right: 10, bottom: 40, left: 30 }

    const svg = d3.select(container).append("svg").attr("width", width).attr("height", height)

    const x = d3
      .scaleBand()
      .domain(data.map((d) => d.range))
      .range([margin.left, width - margin.right])
      .padding(0.2)

    const y = d3
      .scaleLinear()
      .domain([0, d3.max(data, (d) => d.count) || 1])
      .nice()
      .range([height - margin.bottom, margin.top])

    svg
      .selectAll("rect")
      .data(data)
      .join("rect")
      .attr("x", (d) => x(d.range)!)
      .attr("y", (d) => y(d.count))
      .attr("width", x.bandwidth())
      .attr("height", (d) => y(0) - y(d.count))
      .attr("fill", "#0f3460")
      .attr("rx", 2)

    svg
      .append("g")
      .attr("transform", `translate(0,${height - margin.bottom})`)
      .call(d3.axisBottom(x).tickSize(0))
      .call((g) => g.select(".domain").remove())
      .selectAll("text")
      .attr("fill", "#aaa")
      .attr("font-size", "9px")
      .attr("transform", "rotate(-35)")
      .attr("text-anchor", "end")

    svg
      .append("g")
      .attr("transform", `translate(${margin.left},0)`)
      .call(d3.axisLeft(y).ticks(4).tickSize(0))
      .call((g) => g.select(".domain").remove())
      .selectAll("text")
      .attr("fill", "#aaa")
      .attr("font-size", "10px")
  }, [data, h])

  return <div ref={ref} className="w-full" />
}
