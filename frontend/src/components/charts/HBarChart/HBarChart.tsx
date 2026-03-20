import { useEffect, useRef } from "react";
import * as d3 from "d3";
import { useChartSize } from "../useChartSize";
import { ChartTooltip, useTooltip } from "../ChartTooltip";

type HBarChartProps = {
  data: { label: string; value: number }[];
  title?: string;
  color?: "accent" | "success" | "warning" | "danger";
  maxBars?: number;
  height?: number;
  animate?: boolean;
};

const colorVars: Record<string, string> = {
  accent: "var(--color-accent)",
  success: "var(--color-success)",
  warning: "var(--color-warning)",
  danger: "var(--color-danger)",
};

const margin = { top: 4, right: 40, bottom: 4, left: 80 };

export function HBarChart({
  data,
  title,
  color = "accent",
  maxBars,
  height: fixedHeight,
  animate = true,
}: HBarChartProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const { containerRef, width } = useChartSize();
  const { tooltip, show, hide } = useTooltip();

  const displayData = maxBars ? data.slice(0, maxBars) : data;
  const barHeight = 24;
  const gap = 6;
  const computedHeight = fixedHeight ?? displayData.length * (barHeight + gap) + margin.top + margin.bottom;

  useEffect(() => {
    if (!svgRef.current || width === 0) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();

    const innerWidth = width - margin.left - margin.right;
    const innerHeight = computedHeight - margin.top - margin.bottom;

    const x = d3.scaleLinear()
      .domain([0, d3.max(displayData, (d) => d.value) ?? 1])
      .range([0, innerWidth]);

    const y = d3.scaleBand()
      .domain(displayData.map((d) => d.label))
      .range([0, innerHeight])
      .padding(0.2);

    const g = svg.append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`);

    // Labels
    g.selectAll(".label")
      .data(displayData)
      .join("text")
      .attr("class", "label")
      .attr("x", -8)
      .attr("y", (d) => (y(d.label) ?? 0) + y.bandwidth() / 2)
      .attr("text-anchor", "end")
      .attr("dominant-baseline", "central")
      .attr("fill", "var(--color-text-muted)")
      .attr("font-size", "12px")
      .text((d) => d.label);

    // Bars
    const bars = g.selectAll(".bar")
      .data(displayData)
      .join("rect")
      .attr("class", "bar")
      .attr("y", (d) => y(d.label) ?? 0)
      .attr("height", y.bandwidth())
      .attr("rx", 3)
      .attr("fill", colorVars[color]);

    if (animate) {
      bars.attr("width", 0)
        .transition()
        .duration(600)
        .ease(d3.easeCubicOut)
        .attr("width", (d) => x(d.value));
    } else {
      bars.attr("width", (d) => x(d.value));
    }

    // Invisible hit areas for tooltips
    g.selectAll(".hit")
      .data(displayData)
      .join("rect")
      .attr("class", "hit")
      .attr("x", 0)
      .attr("y", (d) => y(d.label) ?? 0)
      .attr("width", innerWidth)
      .attr("height", y.bandwidth())
      .attr("fill", "transparent")
      .attr("cursor", "default")
      .on("mousemove", (event, d) => {
        const [mx, my] = d3.pointer(event, containerRef.current);
        show(d.label, d.value, mx, my);
      })
      .on("mouseleave", hide);

    // Value labels
    g.selectAll(".value")
      .data(displayData)
      .join("text")
      .attr("class", "value")
      .attr("x", (d) => x(d.value) + 6)
      .attr("y", (d) => (y(d.label) ?? 0) + y.bandwidth() / 2)
      .attr("dominant-baseline", "central")
      .attr("fill", "var(--color-text-muted)")
      .attr("font-size", "11px")
      .text((d) => d.value);
  }, [displayData, width, computedHeight, color, animate, show, hide, containerRef]);

  return (
    <div className="bg-bg-secondary border border-border rounded-lg p-4">
      {title && <h3 className="text-sm font-medium text-text-secondary mb-3">{title}</h3>}
      <div ref={containerRef} className="relative w-full" style={{ height: computedHeight }}>
        <svg ref={svgRef} width={width} height={computedHeight} />
        <ChartTooltip tooltip={tooltip} />
      </div>
    </div>
  );
}
