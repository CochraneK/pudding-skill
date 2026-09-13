<script>
	let { bundle } = $props();

	const spec = bundle.spec;
	const chart = bundle.chart;
	const W = 760;
	const H = 420;
	const margin = { top: 34, right: 30, bottom: 74, left: 76 };
	const innerW = W - margin.left - margin.right;
	const innerH = H - margin.top - margin.bottom;

	const number = new Intl.NumberFormat("en", { maximumFractionDigits: 2 });

	function extent(values) {
		const finite = values.filter(Number.isFinite);
		if (!finite.length) return [0, 1];
		let lo = Math.min(...finite);
		let hi = Math.max(...finite);
		if (lo === hi) {
			lo -= 1;
			hi += 1;
		}
		return [lo, hi];
	}

	function scale(value, domain, range) {
		const [d0, d1] = domain;
		const [r0, r1] = range;
		return r0 + ((value - d0) / (d1 - d0)) * (r1 - r0);
	}

	const barValues = chart.type === "bar" || chart.type === "histogram" ? chart.data.map((d) => d.value) : [];
	const barDomain = chart.zero_centered
		? (() => {
			const maxAbs = Math.max(1, ...barValues.map((d) => Math.abs(d)));
			return [-maxAbs, maxAbs];
		})()
		: [Math.min(0, ...barValues), Math.max(1, ...barValues)];

	function barX(value) {
		return scale(value, barDomain, [margin.left, margin.left + innerW]);
	}

	function barZero() {
		return barX(0);
	}

	function barY(index) {
		const band = innerH / Math.max(1, chart.data.length);
		return margin.top + index * band + band * 0.14;
	}

	function barHeight() {
		return (innerH / Math.max(1, chart.data.length)) * 0.72;
	}

	const scatterX = chart.type === "scatter" ? extent(chart.data.map((d) => d.x)) : [0, 1];
	const scatterY = chart.type === "scatter" ? extent(chart.data.map((d) => d.y)) : [0, 1];

	const lineSeries = chart.type === "line"
		? Object.entries(
			chart.data.reduce((acc, d) => {
				(acc[d.series] ||= []).push(d);
				return acc;
			}, {})
		)
		: [];
	const lineX = chart.type === "line" ? [...new Set(chart.data.map((d) => d.x))].sort() : [];
	const lineY = chart.type === "line" ? extent(chart.data.map((d) => d.y)) : [0, 1];

	function linePointX(value) {
		const index = Math.max(0, lineX.indexOf(value));
		return margin.left + (lineX.length <= 1 ? innerW / 2 : (index / (lineX.length - 1)) * innerW);
	}

	function linePointY(value) {
		return scale(value, lineY, [margin.top + innerH, margin.top]);
	}

	function polyline(points) {
		return points.map((d) => `${linePointX(d.x)},${linePointY(d.y)}`).join(" ");
	}
</script>

<article class="auto-story">
	<header class="story-header">
		<p class="eyebrow">AUTO-GENERATED BASELINE · EDITORIAL REVIEW REQUIRED</p>
		<h1>{spec.question}</h1>
		<p class="insight">{spec.primary_insight}</p>
		<div class="meta">
			<span>{bundle.row_count} source rows</span>
			<span>{spec.production_mode || "unspecified mode"}</span>
			<span>{chart.type}</span>
			{#if spec.selection?.score != null}<span>editorial score {spec.selection.score}</span>{/if}
		</div>
		{#if spec.selection}
			<p class="selection-note">Selected from the ranked candidate pool as <strong>#{spec.selection.rank}</strong>. <a href="/lab">Inspect the editorial decision →</a></p>
		{/if}
	</header>

	<section class="narrative-grid">
		<div class="beats">
			<p class="section-label">Narrative beats</p>
			{#each spec.beats as beat, i}
				<article class="beat">
					<span>{String(i + 1).padStart(2, "0")}</span>
					<div>
						<strong>{beat.operation || "beat"}</strong>
						<p>{beat.purpose}</p>
					</div>
				</article>
			{/each}
		</div>

		<div class="chart-card">
			<div class="chart-head">
				<p class="section-label">Evidence view</p>
				<h2>{spec.visuals[0].purpose}</h2>
			</div>

			<svg viewBox={`0 0 ${W} ${H}`} role="img" aria-labelledby="auto-title auto-desc">
				<title id="auto-title">{spec.primary_insight}</title>
				<desc id="auto-desc">Automatically generated {chart.type} chart based on {bundle.source_file}.</desc>

				{#if chart.type === "bar" || chart.type === "histogram"}
					<line x1={barZero()} x2={barZero()} y1={margin.top - 10} y2={margin.top + innerH + 12} class="axis" />
					{#each chart.data as d, i}
						{@const x = Math.min(barZero(), barX(d.value))}
						{@const width = Math.abs(barX(d.value) - barZero())}
						<g>
							<rect x={x} y={barY(i)} width={Math.max(1, width)} height={barHeight()} rx="3" />
							<text x={margin.left - 12} y={barY(i) + barHeight() / 2 + 5} text-anchor="end" class="label">{d.label}</text>
							<text x={d.value >= 0 ? barX(d.value) + 8 : barX(d.value) - 8} y={barY(i) + barHeight() / 2 + 5} text-anchor={d.value >= 0 ? "start" : "end"} class="value">{number.format(d.value)}</text>
						</g>
					{/each}
					<text x={margin.left + innerW / 2} y={H - 18} text-anchor="middle" class="axis-label">{chart.y_label}</text>
				{:else if chart.type === "scatter"}
					<line x1={margin.left} x2={margin.left} y1={margin.top} y2={margin.top + innerH} class="axis" />
					<line x1={margin.left} x2={margin.left + innerW} y1={margin.top + innerH} y2={margin.top + innerH} class="axis" />
					{#each chart.data as d}
						<circle cx={scale(d.x, scatterX, [margin.left, margin.left + innerW])} cy={scale(d.y, scatterY, [margin.top + innerH, margin.top])} r="5" />
					{/each}
					<text x={margin.left + innerW / 2} y={H - 18} text-anchor="middle" class="axis-label">{chart.x_label}</text>
					<text transform={`translate(18 ${margin.top + innerH / 2}) rotate(-90)`} text-anchor="middle" class="axis-label">{chart.y_label}</text>
				{:else if chart.type === "line"}
					<line x1={margin.left} x2={margin.left} y1={margin.top} y2={margin.top + innerH} class="axis" />
					<line x1={margin.left} x2={margin.left + innerW} y1={margin.top + innerH} y2={margin.top + innerH} class="axis" />
					{#each lineSeries as [series, points], i}
						<polyline points={polyline(points)} class={`series series-${i % 6}`} />
						{#each points as d}
							<circle cx={linePointX(d.x)} cy={linePointY(d.y)} r="4" class={`dot series-${i % 6}`} />
						{/each}
						{@const last = points[points.length - 1]}
						<text x={linePointX(last.x) + 8} y={linePointY(last.y) + 4} class="label">{series}</text>
					{/each}
					{#each lineX as value}
						<text x={linePointX(value)} y={margin.top + innerH + 24} text-anchor="middle" class="tick">{value}</text>
					{/each}
					<text x={margin.left + innerW / 2} y={H - 18} text-anchor="middle" class="axis-label">{chart.x_label}</text>
				{/if}
			</svg>

			<p class="chart-caption">Source: {bundle.source_file}. This renderer is a baseline, not a publication-ready editorial graphic.</p>
		</div>
	</section>

	<section class="audit">
		<div>
			<p class="section-label">Caveats</p>
			<ul>
				{#each spec.caveats as caveat}<li>{caveat}</li>{/each}
			</ul>
		</div>
		<div>
			<p class="section-label">Sources</p>
			<ul>
				{#each spec.sources as source}<li>{typeof source === "string" ? source : source.label}</li>{/each}
			</ul>
		</div>
	</section>

	<details class="data-table">
		<summary>Inspect chart data</summary>
		<div class="table-scroll">
			<table>
				<thead>
					<tr>
						{#each Object.keys(chart.data[0] || {}) as key}<th>{key}</th>{/each}
					</tr>
				</thead>
				<tbody>
					{#each chart.data as row}
						<tr>{#each Object.keys(chart.data[0] || {}) as key}<td>{row[key]}</td>{/each}</tr>
					{/each}
				</tbody>
			</table>
		</div>
	</details>
</article>

<style>
	.auto-story { width: min(1180px, calc(100% - 40px)); margin: 0 auto; padding-bottom: 10vh; }
	.story-header { max-width: 920px; padding: 9vh 0 7vh; }
	.eyebrow, .section-label, .meta { font-family: var(--font-mono); text-transform: uppercase; letter-spacing: .08em; font-size: .72rem; font-weight: 700; }
	.eyebrow, .section-label { color: #b7452a; }
	h1 { font-family: var(--font-serif); font-size: clamp(2.6rem, 7vw, 6.3rem); line-height: .96; letter-spacing: -.045em; margin: .15em 0 .35em; }
	.insight { max-width: 760px; font-size: clamp(1.15rem, 2vw, 1.5rem); line-height: 1.5; color: #55524e; }
	.meta { display: flex; flex-wrap: wrap; gap: .55rem 1.2rem; margin-top: 2rem; color: #6f6b65; }
	.selection-note { margin: 1.1rem 0 0; font-family: var(--font-sans); font-size: .86rem; color: #6f6b65; }
	.selection-note a { color: #b7452a; font-weight: 700; text-decoration: none; }
	.narrative-grid { display: grid; grid-template-columns: minmax(240px, .72fr) minmax(0, 1.7fr); gap: clamp(2rem, 5vw, 5rem); align-items: start; border-top: 1px solid #d9d3c9; padding-top: 4rem; }
	.beats { position: sticky; top: 2rem; }
	.beat { display: grid; grid-template-columns: 2.2rem 1fr; gap: .8rem; padding: 1rem 0; border-bottom: 1px solid #e2ddd4; }
	.beat > span { font-family: var(--font-mono); font-size: .7rem; color: #8f8a82; }
	.beat strong { font-family: var(--font-sans); text-transform: uppercase; font-size: .78rem; letter-spacing: .05em; }
	.beat p { margin: .3rem 0 0; line-height: 1.45; color: #5d5954; }
	.chart-card { background: #fffdf8; border: 1px solid #ded8cf; border-radius: 16px; padding: clamp(1rem, 3vw, 2rem); box-shadow: 0 18px 50px rgba(36, 31, 25, .05); }
	.chart-head h2 { max-width: 680px; font-family: var(--font-serif); font-size: clamp(1.45rem, 2.8vw, 2.2rem); margin: .25rem 0 1.5rem; }
	svg { overflow: visible; }
	rect, circle { fill: #c74c2e; }
	.axis { stroke: #aaa49a; stroke-width: 1; }
	.label, .value, .tick, .axis-label { font-family: var(--font-sans); fill: #35322f; }
	.label { font-size: 13px; font-weight: 650; }
	.value { font-size: 12px; font-weight: 700; }
	.tick { font-size: 11px; fill: #716c65; }
	.axis-label { font-size: 12px; fill: #716c65; }
	.series { fill: none; stroke: #c74c2e; stroke-width: 3; }
	.series-1 { stroke: #356b73; fill: #356b73; }
	.series-2 { stroke: #8a6b2c; fill: #8a6b2c; }
	.series-3 { stroke: #745383; fill: #745383; }
	.series-4 { stroke: #5b7540; fill: #5b7540; }
	.series-5 { stroke: #8a4c58; fill: #8a4c58; }
	.dot { stroke: #fffdf8; stroke-width: 2; }
	.chart-caption { margin: 1rem 0 0; font-family: var(--font-sans); font-size: .78rem; color: #77716a; }
	.audit { display: grid; grid-template-columns: 1fr 1fr; gap: 3rem; margin-top: 4rem; border-top: 1px solid #d9d3c9; padding-top: 2.5rem; }
	.audit ul { padding-left: 1.2rem; line-height: 1.55; color: #55524e; }
	.data-table { margin-top: 3rem; border-top: 1px solid #d9d3c9; padding-top: 1.5rem; font-family: var(--font-sans); }
	.data-table summary { cursor: pointer; font-weight: 700; }
	.table-scroll { overflow-x: auto; margin-top: 1rem; }
	table { border-collapse: collapse; width: 100%; font-size: .8rem; }
	th, td { text-align: left; padding: .6rem .8rem; border-bottom: 1px solid #e4dfd7; white-space: nowrap; }
	th { font-family: var(--font-mono); font-size: .7rem; text-transform: uppercase; }
	@media (max-width: 760px) {
		.auto-story { width: min(100% - 28px, 680px); }
		.narrative-grid { grid-template-columns: 1fr; }
		.beats { position: static; }
		.chart-card { padding: 1rem .7rem 1rem; }
		.audit { grid-template-columns: 1fr; gap: 1rem; }
		h1 { font-size: clamp(2.5rem, 13vw, 4.5rem); }
	}
	@media (prefers-reduced-motion: reduce) { * { scroll-behavior: auto !important; transition: none !important; animation: none !important; } }
</style>
