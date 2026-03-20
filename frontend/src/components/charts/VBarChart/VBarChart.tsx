import { useEffect, useRef } from "react";
import * as d3 from "d3";
import { useChartSize } from "../useChartSize";
import { ChartTooltip, useTooltip } from "../ChartTooltip";

type VBarChartProps = {
  data: { label: string; value: number }[];
  title?: string;
  color?: "accent" | "success" | "warning" | "danger";
  height?: number;
  animate?: boolean;
};

const colorVars: Record<string, string> = {
  accent: "var(--color-accent)",
  success: "var(--color-success)",
  warning: "var(--color-warning)",
  danger: "var(--color-danger)",
};

const margin = { top: 8, right: 8, bottom: 28, left: 32 };

export function VBarChart({
  data,
  title,
  color = "accent",
  height: fixedHeight = 200,
  animate = true,
}: VBarChartProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const { containerRef, width } = useChartSize();
  const { tooltip, show, hide } = useTooltip();

  useEffect(() => {
    if (!svgRef.current || width === 0) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();

    const innerWidth = width - margin.left - margin.right;
    const innerHeight = fixedHeight - margin.top - margin.bottom;

    const x = d3.scaleBand()
      .domain(data.map((d) => d.label))
      .range([0, innerWidth])
      .padding(0.25);

    const y = d3.scaleLinear()
      .domain([0, d3.max(data, (d) => d.value) ?? 1])
      .nice()
      .range([innerHeight, 0]);

    const g = svg.append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`);

    // Grid lines
    g.selectAll(".grid")
      .data(y.ticks(5))
      .join("line")
      .attr("class", "grid")
      .attr("x1", 0)
      .attr("x2", innerWidth)
      .attr("y1", (d) => y(d))
      .attr("y2", (d) => y(d))
      .attr("stroke", "var(--color-border)")
      .attr("stroke-dasharray", "2,3");

    // Bars
    const bars = g.selectAll(".bar")
      .data(data)
      .join("rect")
      .attr("class", "bar")
      .attr("x", (d) => x(d.label) ?? 0)
      .attr("width", x.bandwidth())
      .attr("rx", 3)
      .attr("fill", colorVars[color]);

    if (animate) {
      bars
        .attr("y", innerHeight)
        .attr("height", 0)
        .transition()
        .duration(600)
        .ease(d3.easeCubicOut)
        .attr("y", (d) => y(d.value))
        .attr("height", (d) => innerHeight - y(d.value));
    } else {
      bars
        .attr("y", (d) => y(d.value))
        .attr("height", (d) => innerHeight - y(d.value));
    }

    // Hit areas
    g.selectAll(".hit")
      .data(data)
      .join("rect")
      .attr("class", "hit")
      .attr("x", (d) => x(d.label) ?? 0)
      .attr("width", x.bandwidth())
      .attr("y", 0)
      .attr("height", innerHeight)
      .attr("fill", "transparent")
      .attr("cursor", "default")
      .on("mousemove", (event, d) => {
        const [mx, my] = d3.pointer(event, containerRef.current);
        show(d.label, d.value, mx, my);
      })
      .on("mouseleave", hide);

    // X axis labels
    g.append("g")
      .attr("transform", `translate(0,${innerHeight})`)
      .call(d3.axisBottom(x).tickSize(0).tickPadding(8))
      .call((g) => g.select(".domain").remove())
      .selectAll("text")
      .attr("fill", "var(--color-text-muted)")
      .attr("font-size", "11px");

    // Y axis labels
    g.append("g")
      .call(d3.axisLeft(y).ticks(5).tickSize(0).tickPadding(6))
      .call((g) => g.select(".domain").remove())
      .selectAll("text")
      .attr("fill", "var(--color-text-muted)")
      .attr("font-size", "11px");
  }, [data, width, fixedHeight, color, animate, show, hide, containerRef]);

  return (
    <div className="bg-bg-secondary border border-border rounded-lg p-4">
      {title && <h3 className="text-sm font-medium text-text-secondary mb-3">{title}</h3>}
      <div ref={containerRef} className="relative w-full" style={{ height: fixedHeight }}>
        <svg ref={svgRef} width={width} height={fixedHeight} />
        <ChartTooltip tooltip={tooltip} />
      </div>
    </div>
  );
}
