import { useEffect, useRef } from "react";
import * as d3 from "d3";
import { useChartSize } from "../useChartSize";
import { ChartTooltip, useTooltip } from "../ChartTooltip";

type DonutChartProps = {
  data: { label: string; value: number; color?: string }[];
  title?: string;
  size?: number;
  innerRadiusRatio?: number;
  animate?: boolean;
  showLabels?: boolean;
  showLegend?: boolean;
};

const PALETTE = [
  "var(--color-accent)",
  "var(--color-success)",
  "var(--color-warning)",
  "var(--color-danger)",
  "var(--color-text-secondary)",
  "var(--color-text-muted)",
  "var(--color-accent-hover)",
  "var(--color-border-hover)",
];

export function DonutChart({
  data,
  title,
  size: fixedSize = 220,
  innerRadiusRatio = 0.55,
  animate = true,
  showLabels = true,
  showLegend = true,
}: DonutChartProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const { containerRef } = useChartSize();
  const { tooltip, show, hide } = useTooltip();

  const total = data.reduce((sum, d) => sum + d.value, 0);

  useEffect(() => {
    if (!svgRef.current) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();

    const radius = fixedSize / 2;
    const innerRadius = radius * innerRadiusRatio;

    const g = svg.append("g")
      .attr("transform", `translate(${radius},${radius})`);

    const pie = d3.pie<{ label: string; value: number; color?: string }>()
      .value((d) => d.value)
      .sort(null)
      .padAngle(0.02);

    const arc = d3.arc<d3.PieArcDatum<{ label: string; value: number; color?: string }>>()
      .innerRadius(innerRadius)
      .outerRadius(radius - 2)
      .cornerRadius(3);

    const arcs = pie(data);

    const paths = g.selectAll("path")
      .data(arcs)
      .join("path")
      .attr("fill", (_, i) => data[i].color ?? PALETTE[i % PALETTE.length])
      .attr("cursor", "default")
      .on("mousemove", (event, d) => {
        const [mx, my] = d3.pointer(event, containerRef.current);
        const pct = ((d.data.value / total) * 100).toFixed(1);
        show(d.data.label, `${d.data.value} (${pct}%)`, mx, my);
      })
      .on("mouseleave", hide);

    if (animate) {
      paths.each(function (d) {
        const path = d3.select(this);
        const start = { ...d, startAngle: d.startAngle, endAngle: d.startAngle };
        const interpolate = d3.interpolate(start, d);
        path
          .attr("d", arc(start)!)
          .transition()
          .duration(700)
          .ease(d3.easeCubicOut)
          .attrTween("d", () => (t) => arc(interpolate(t))!);
      });
    } else {
      paths.attr("d", (d) => arc(d)!);
    }

    // Center total
    if (showLabels) {
      g.append("text")
        .attr("text-anchor", "middle")
        .attr("dominant-baseline", "central")
        .attr("fill", "var(--color-text-primary)")
        .attr("font-size", "20px")
        .attr("font-weight", "bold")
        .text(total);
    }
  }, [data, fixedSize, innerRadiusRatio, animate, total, show, hide, showLabels, containerRef]);

  return (
    <div className="bg-bg-secondary border border-border rounded-lg p-4">
      {title && <h3 className="text-sm font-medium text-text-secondary mb-3">{title}</h3>}
      <div ref={containerRef} className="relative flex items-start gap-4">
        <svg ref={svgRef} width={fixedSize} height={fixedSize} className="shrink-0" />
        {showLegend && (
          <div className="flex flex-col gap-1.5 py-2">
            {data.map((d, i) => (
              <div key={d.label} className="flex items-center gap-2 text-xs">
                <span
                  className="w-3 h-3 rounded-sm shrink-0"
                  style={{ backgroundColor: d.color ?? PALETTE[i % PALETTE.length] }}
                />
                <span className="text-text-muted">{d.label}</span>
                <span className="text-text-secondary font-medium ml-auto pl-3">{d.value}</span>
              </div>
            ))}
          </div>
        )}
        <ChartTooltip tooltip={tooltip} />
      </div>
    </div>
  );
}
