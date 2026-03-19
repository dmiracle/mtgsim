import * as d3 from "d3"
import { useEffect, useRef } from "react"

interface Props {
  data: Record<string, number>
}

export default function ManaCurveChart({ data }: Props) {
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!ref.current) return
    const container = ref.current
    container.innerHTML = ""

    const entries = Object.entries(data)
      .map(([k, v]) => ({ mv: k, count: v }))
      .sort((a, b) => Number(a.mv) - Number(b.mv))

    if (entries.length === 0) return

    const width = container.clientWidth
    const height = 160
    const margin = { top: 10, right: 10, bottom: 25, left: 30 }

    const svg = d3.select(container).append("svg").attr("width", width).attr("height", height)

    const x = d3
      .scaleBand()
      .domain(entries.map((d) => d.mv))
      .range([margin.left, width - margin.right])
      .padding(0.3)

    const y = d3
      .scaleLinear()
      .domain([0, d3.max(entries, (d) => d.count) || 1])
      .nice()
      .range([height - margin.bottom, margin.top])

    svg
      .selectAll("rect")
      .data(entries)
      .join("rect")
      .attr("x", (d) => x(d.mv)!)
      .attr("y", (d) => y(d.count))
      .attr("width", x.bandwidth())
      .attr("height", (d) => y(0) - y(d.count))
      .attr("fill", "#e94560")
      .attr("rx", 2)

    svg
      .selectAll(".label")
      .data(entries)
      .join("text")
      .attr("x", (d) => x(d.mv)! + x.bandwidth() / 2)
      .attr("y", (d) => y(d.count) - 3)
      .attr("text-anchor", "middle")
      .attr("fill", "#aaa")
      .attr("font-size", "10px")
      .text((d) => d.count)

    svg
      .append("g")
      .attr("transform", `translate(0,${height - margin.bottom})`)
      .call(d3.axisBottom(x).tickSize(0))
      .call((g) => g.select(".domain").remove())
      .selectAll("text")
      .attr("fill", "#aaa")
      .attr("font-size", "10px")
  }, [data])

  return <div ref={ref} className="w-full" />
}
