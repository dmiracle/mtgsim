import { useEffect, useRef } from "react";
import * as d3 from "d3";
import { ChartTooltip, useTooltip } from "../ChartTooltip";

type RadarChartProps = {
  data: { axis: string; value: number }[];
  title?: string;
  maxValue?: number;
  size?: number;
  levels?: number;
  color?: "accent" | "success" | "warning" | "danger";
  animate?: boolean;
  interactive?: boolean;
  snapIncrement?: number;
  onValueChange?: (index: number, value: number) => void;
  onDrag?: (index: number, value: number) => void;
};

const colorVars: Record<string, string> = {
  accent: "var(--color-accent)",
  success: "var(--color-success)",
  warning: "var(--color-warning)",
  danger: "var(--color-danger)",
};

export function RadarChart({
  data,
  title,
  maxValue = 5,
  size: fixedSize = 260,
  levels = 5,
  color = "accent",
  animate = true,
  interactive = false,
  snapIncrement = 0.01,
  onValueChange,
  onDrag,
}: RadarChartProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const { tooltip, show, hide } = useTooltip();

  // Refs to avoid re-renders during drag
  const onChangeRef = useRef(onValueChange);
  onChangeRef.current = onValueChange;
  const onDragRef = useRef(onDrag);
  onDragRef.current = onDrag;
  const draggingRef = useRef(false);

  // Only re-render from props when not dragging
  const dataRef = useRef(data);
  if (!draggingRef.current) {
    dataRef.current = data;
  }

  useEffect(() => {
    if (!svgRef.current) return;
    if (draggingRef.current) return; // Skip re-render during drag

    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();

    const labelPad = 70;
    const radius = fixedSize / 2;
    const svgW = fixedSize + labelPad * 2;
    const svgH = fixedSize + labelPad * 2;
    const cx = svgW / 2;
    const cy = svgH / 2;

    svg
      .attr("viewBox", `0 0 ${svgW} ${svgH}`)
      .attr("width", "100%")
      .attr("height", "auto")
      .style("max-width", `${svgW}px`);

    const n = data.length;
    const angleSlice = (Math.PI * 2) / n;

    const rScale = d3.scaleLinear()
      .domain([0, maxValue])
      .range([0, radius]);

    const g = svg.append("g")
      .attr("transform", `translate(${cx},${cy})`);

    // Mutable live values — D3 owns these during drag
    const liveValues = data.map((d) => d.value);

    // Grid circles
    for (let level = 1; level <= levels; level++) {
      const r = (radius / levels) * level;
      g.append("circle")
        .attr("r", r)
        .attr("fill", "none")
        .attr("stroke", "var(--color-border)")
        .attr("stroke-dasharray", "2,3");
    }

    // Grid level labels
    for (let level = 1; level <= levels; level++) {
      const r = (radius / levels) * level;
      g.append("text")
        .attr("x", 4)
        .attr("y", -r)
        .attr("fill", "var(--color-text-muted)")
        .attr("font-size", "9px")
        .attr("dominant-baseline", "auto")
        .text(((maxValue / levels) * level).toFixed(1));
    }

    // Axis lines + labels + value labels
    const valueLabelNodes: d3.Selection<SVGTextElement, unknown, null, undefined>[] = [];
    data.forEach((d, i) => {
      const angle = angleSlice * i - Math.PI / 2;
      const x2 = Math.cos(angle) * radius;
      const y2 = Math.sin(angle) * radius;

      g.append("line")
        .attr("x1", 0).attr("y1", 0)
        .attr("x2", x2).attr("y2", y2)
        .attr("stroke", "var(--color-border)")
        .attr("stroke-width", 1);

      const labelR = radius + 18;
      const lx = Math.cos(angle) * labelR;
      const ly = Math.sin(angle) * labelR;
      const anchor = Math.abs(lx) < 1 ? "middle" : lx > 0 ? "start" : "end";

      g.append("text")
        .attr("x", lx)
        .attr("y", ly)
        .attr("text-anchor", anchor)
        .attr("dominant-baseline", "central")
        .attr("fill", "var(--color-text-secondary)")
        .attr("font-size", "12px")
        .attr("font-weight", "500")
        .text(d.axis);

      if (interactive) {
        const vlOffset = Math.abs(ly) < 1 ? 14 : ly > 0 ? 14 : -14;
        const valueLabel = g.append("text")
          .attr("x", lx)
          .attr("y", ly + vlOffset)
          .attr("text-anchor", anchor)
          .attr("dominant-baseline", "central")
          .attr("fill", "var(--color-accent)")
          .attr("font-size", "11px")
          .attr("font-weight", "700")
          .text(d.value > 0 ? d.value.toFixed(1) : "—");
        valueLabelNodes.push(valueLabel);
      }
    });

    // Polygon
    const fillColor = colorVars[color];
    const lineGen = d3.line<[number, number]>()
      .x((d) => d[0])
      .y((d) => d[1])
      .curve(d3.curveLinearClosed);

    function getPoints(): [number, number][] {
      return liveValues.map((v, i) => {
        const angle = angleSlice * i - Math.PI / 2;
        return [Math.cos(angle) * rScale(v), Math.sin(angle) * rScale(v)];
      });
    }

    const polygon = g.append("path")
      .attr("fill", fillColor)
      .attr("fill-opacity", 0.2)
      .attr("stroke", fillColor)
      .attr("stroke-width", 2);

    if (animate && !interactive) {
      const zeroPoints = data.map(() => [0, 0] as [number, number]);
      polygon
        .attr("d", lineGen(zeroPoints))
        .transition().duration(700).ease(d3.easeCubicOut)
        .attr("d", lineGen(getPoints()));
    } else {
      polygon.attr("d", lineGen(getPoints()));
    }

    // Data points
    const pointNodes: d3.Selection<SVGCircleElement, unknown, null, undefined>[] = [];
    data.forEach((d, i) => {
      const angle = angleSlice * i - Math.PI / 2;
      const px = Math.cos(angle) * rScale(d.value);
      const py = Math.sin(angle) * rScale(d.value);

      const point = g.append("circle")
        .attr("cx", px)
        .attr("cy", py)
        .attr("r", interactive ? 8 : 5)
        .attr("fill", fillColor)
        .attr("stroke", "var(--color-bg-secondary)")
        .attr("stroke-width", 2)
        .attr("cursor", interactive ? "grab" : "default");

      pointNodes.push(point);

      if (interactive) {
        point
          .on("mouseenter", function () { d3.select(this).attr("r", 10).attr("stroke-width", 3); })
          .on("mouseleave", function () { d3.select(this).attr("r", 8).attr("stroke-width", 2); });

        const drag = d3.drag<SVGCircleElement, unknown>()
          .on("start", function () {
            draggingRef.current = true;
            d3.select(this).attr("cursor", "grabbing").attr("r", 10);
          })
          .on("drag", function (event) {
            const axisX = Math.cos(angle);
            const axisY = Math.sin(angle);
            const projection = event.x * axisX + event.y * axisY;
            const clamped = Math.max(0, Math.min(radius, projection));
            const val = Math.max(0, Math.min(maxValue, Math.round(rScale.invert(clamped) * 100) / 100));

            liveValues[i] = val;

            // Update point position immediately
            const newR = rScale(val);
            d3.select(this)
              .attr("cx", Math.cos(angle) * newR)
              .attr("cy", Math.sin(angle) * newR);

            // Update polygon immediately
            polygon.attr("d", lineGen(getPoints()));

            // Update value label immediately
            if (valueLabelNodes[i]) {
              valueLabelNodes[i].text(val > 0 ? val.toFixed(1) : "—");
            }

            // Notify parent of live value
            onDragRef.current?.(i, val);
          })
          .on("end", function () {
            d3.select(this).attr("cursor", "grab").attr("r", 8);

            // Snap on release
            const snapped = Math.round(liveValues[i] / snapIncrement) * snapIncrement;
            const final = Math.max(0, Math.min(maxValue, Math.round(snapped * 100) / 100));
            liveValues[i] = final;

            const newR = rScale(final);
            d3.select(this)
              .transition().duration(80)
              .attr("cx", Math.cos(angle) * newR)
              .attr("cy", Math.sin(angle) * newR);

            polygon.transition().duration(80)
              .attr("d", lineGen(getPoints()));

            if (valueLabelNodes[i]) {
              valueLabelNodes[i].text(final > 0 ? final.toFixed(1) : "—");
            }

            // Release drag lock, then notify React
            draggingRef.current = false;
            onChangeRef.current?.(i, final);
          });

        point.call(drag);
      } else {
        point
          .on("mousemove", (event) => {
            const [mx, my] = d3.pointer(event, containerRef.current);
            show(d.axis, `${d.value} / ${maxValue}`, mx, my);
          })
          .on("mouseleave", hide);
      }
    });

    // Click on axis to set value
    if (interactive) {
      data.forEach((_, i) => {
        const angle = angleSlice * i - Math.PI / 2;
        g.append("line")
          .attr("x1", 0).attr("y1", 0)
          .attr("x2", Math.cos(angle) * radius)
          .attr("y2", Math.sin(angle) * radius)
          .attr("stroke", "transparent")
          .attr("stroke-width", 20)
          .attr("cursor", "pointer")
          .on("click", (event) => {
            const [mx, my] = d3.pointer(event, g.node());
            const axisX = Math.cos(angle);
            const axisY = Math.sin(angle);
            const projection = mx * axisX + my * axisY;
            const clamped = Math.max(0, Math.min(radius, projection));
            const snapped = Math.round(rScale.invert(clamped) / snapIncrement) * snapIncrement;
            const final = Math.max(0, Math.min(maxValue, Math.round(snapped * 100) / 100));

            liveValues[i] = final;

            const newR = rScale(final);
            pointNodes[i].transition().duration(150)
              .attr("cx", Math.cos(angle) * newR)
              .attr("cy", Math.sin(angle) * newR);

            polygon.transition().duration(150)
              .attr("d", lineGen(getPoints()));

            if (valueLabelNodes[i]) {
              valueLabelNodes[i].text(final > 0 ? final.toFixed(1) : "—");
            }

            onChangeRef.current?.(i, final);
          });
      });
    }
  }, [data, fixedSize, maxValue, levels, color, animate, interactive, snapIncrement, show, hide]);

  return (
    <div className="bg-bg-secondary border border-border rounded-lg p-4">
      {title && <h3 className="text-sm font-medium text-text-secondary mb-3">{title}</h3>}
      <div ref={containerRef} className="relative flex justify-center">
        <svg ref={svgRef} />
        <ChartTooltip tooltip={tooltip} />
      </div>
    </div>
  );
}
