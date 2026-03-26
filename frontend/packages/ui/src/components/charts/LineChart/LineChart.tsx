import { useEffect, useRef } from "react";
import * as d3 from "d3";
import { useChartSize } from "../useChartSize";
import { ChartTooltip, useTooltip } from "../ChartTooltip";

type LineChartSeries = {
  label: string;
  color: string;
  data: { x: string; y: number }[];
};

type LineChartProps = {
  series: LineChartSeries[];
  title?: string;
  height?: number;
  yLabel?: string;
  animate?: boolean;
};

const margin = { top: 8, right: 12, bottom: 32, left: 40 };

export function LineChart({
  series,
  title,
  height: fixedHeight = 200,
  yLabel,
  animate = true,
}: LineChartProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const { containerRef, width } = useChartSize();
  const { tooltip, show, hide } = useTooltip();

  useEffect(() => {
    if (!svgRef.current || width === 0 || series.length === 0) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();

    const innerWidth = width - margin.left - margin.right;
    const innerHeight = fixedHeight - margin.top - margin.bottom;

    // Collect all x values
    const allX = [...new Set(series.flatMap((s) => s.data.map((d) => d.x)))];
    const allY = series.flatMap((s) => s.data.map((d) => d.y));

    const x = d3.scalePoint().domain(allX).range([0, innerWidth]).padding(0.5);
    const y = d3.scaleLinear().domain([0, d3.max(allY) ?? 1]).nice().range([innerHeight, 0]);

    const g = svg.append("g").attr("transform", `translate(${margin.left},${margin.top})`);

    // Grid lines
    g.selectAll(".grid")
      .data(y.ticks(5))
      .join("line")
      .attr("x1", 0).attr("x2", innerWidth)
      .attr("y1", (d) => y(d)).attr("y2", (d) => y(d))
      .attr("stroke", "var(--color-border)")
      .attr("stroke-dasharray", "2,3");

    // X axis
    const xAxis = g.append("g")
      .attr("transform", `translate(0,${innerHeight})`)
      .call(d3.axisBottom(x).tickSize(0).tickPadding(8));
    xAxis.select(".domain").remove();
    xAxis.selectAll("text")
      .attr("fill", "var(--color-text-muted)")
      .attr("font-size", "10px")
      .attr("transform", "rotate(-45)")
      .attr("text-anchor", "end");

    // Y axis
    const yAxis = g.append("g")
      .call(d3.axisLeft(y).ticks(5).tickSize(0).tickPadding(6));
    yAxis.select(".domain").remove();
    yAxis.selectAll("text").attr("fill", "var(--color-text-muted)").attr("font-size", "10px");

    if (yLabel) {
      g.append("text")
        .attr("transform", "rotate(-90)")
        .attr("x", -innerHeight / 2).attr("y", -30)
        .attr("text-anchor", "middle")
        .attr("fill", "var(--color-text-muted)")
        .attr("font-size", "10px")
        .text(yLabel);
    }

    // Lines + dots per series
    const line = d3.line<{ x: string; y: number }>()
      .x((d) => x(d.x) ?? 0)
      .y((d) => y(d.y))
      .curve(d3.curveMonotoneX);

    for (const s of series) {
      const path = g.append("path")
        .datum(s.data)
        .attr("fill", "none")
        .attr("stroke", s.color)
        .attr("stroke-width", 2)
        .attr("d", line);

      if (animate) {
        const totalLen = (path.node() as SVGPathElement)?.getTotalLength() ?? 0;
        path
          .attr("stroke-dasharray", `${totalLen} ${totalLen}`)
          .attr("stroke-dashoffset", totalLen)
          .transition().duration(800).ease(d3.easeCubicOut)
          .attr("stroke-dashoffset", 0);
      }

      // Dots
      g.selectAll(`.dot-${s.label}`)
        .data(s.data)
        .join("circle")
        .attr("cx", (d) => x(d.x) ?? 0)
        .attr("cy", (d) => y(d.y))
        .attr("r", 3)
        .attr("fill", s.color)
        .attr("stroke", "var(--color-bg-secondary)")
        .attr("stroke-width", 1.5)
        .attr("cursor", "default")
        .on("mousemove", (event, d) => {
          const [mx, my] = d3.pointer(event, containerRef.current);
          show(`${s.label}: ${d.x}`, d.y, mx, my);
        })
        .on("mouseleave", hide);
    }

    // Legend
    if (series.length > 1) {
      const legend = g.append("g").attr("transform", `translate(${innerWidth - 10}, 0)`);
      series.forEach((s, i) => {
        const row = legend.append("g").attr("transform", `translate(0, ${i * 16})`);
        row.append("line").attr("x1", -20).attr("x2", -8).attr("y1", 0).attr("y2", 0)
          .attr("stroke", s.color).attr("stroke-width", 2);
        row.append("text").attr("x", -4).attr("y", 4).attr("text-anchor", "end")
          .attr("fill", "var(--color-text-muted)").attr("font-size", "9px").text(s.label);
      });
    }
  }, [series, width, fixedHeight, yLabel, animate, show, hide, containerRef]);

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
