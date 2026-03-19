import * as d3 from "d3"
import cloud from "d3-cloud"
import { useEffect, useRef } from "react"

interface Props {
  words: Record<string, number>
  onWordClick?: (word: string) => void
  selectedWords?: string[]
  width?: number
  height?: number
}

export default function WordCloud({ words, onWordClick, selectedWords = [], width: w, height: h = 200 }: Props) {
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!ref.current) return
    const container = ref.current
    container.innerHTML = ""

    const entries = Object.entries(words)
    if (entries.length === 0) return

    const width = w || container.clientWidth
    const height = h
    const maxCount = Math.max(...entries.map(([, c]) => c))
    const minCount = Math.min(...entries.map(([, c]) => c))

    const fontSize = d3
      .scaleLinear()
      .domain([minCount, maxCount])
      .range([11, 28])

    const wordData = entries.map(([text, count]) => ({
      text,
      size: fontSize(count),
      count,
    }))

    const layout = cloud()
      .size([width, height])
      .words(wordData as cloud.Word[])
      .padding(3)
      .rotate(0)
      .fontSize((d) => (d as unknown as { size: number }).size)
      .on("end", draw)

    layout.start()

    function draw(layoutWords: cloud.Word[]) {
      const svg = d3
        .select(container)
        .append("svg")
        .attr("width", width)
        .attr("height", height)

      const g = svg
        .append("g")
        .attr("transform", `translate(${width / 2},${height / 2})`)

      g.selectAll("text")
        .data(layoutWords)
        .join("text")
        .style("font-size", (d) => `${d.size}px`)
        .style("fill", (d) =>
          selectedWords.includes(d.text!) ? "#e94560" : "#8899bb",
        )
        .style("cursor", onWordClick ? "pointer" : "default")
        .style("font-weight", (d) =>
          selectedWords.includes(d.text!) ? "bold" : "normal",
        )
        .attr("text-anchor", "middle")
        .attr("transform", (d) => `translate(${d.x},${d.y})`)
        .text((d) => d.text!)
        .on("click", (_, d) => onWordClick?.(d.text!))
        .append("title")
        .text((d) => `${d.text}: ${(d as unknown as { count: number }).count}`)
    }
  }, [words, onWordClick, selectedWords, w, h])

  return <div ref={ref} className="w-full" />
}
