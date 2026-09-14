<script>
	import { geoNaturalEarth1, geoPath, scaleLinear, scaleSymlog } from 'd3';
	import capacity from '$data/global-mental-health-capacity.json';
	import worldRaw from '$data/world-110m.geojson?raw';

	const world = JSON.parse(worldRaw);
	const countryByCode = new Map(capacity.countries.map((country) => [country.code, country]));
	const metricOptions = [
		'psychiatrists_per_100k',
		'mental_health_nurses_per_100k',
		'psychologists_per_100k',
		'mental_health_outpatient_facilities_per_100k',
		'government_mental_health_spending_share'
	];
	let selectedMetric = $state('psychiatrists_per_100k');

	const projection = geoNaturalEarth1().fitExtent(
		[
			[12, 12],
			[948, 468]
		],
		world
	);
	const path = geoPath(projection);

	const codeForFeature = (feature) => {
		const props = feature.properties || {};
		const candidates = [props.code, props.iso_a3_eh, props.iso_a3];
		return candidates.find((code) => code && code !== '-99') || null;
	};
	const countryForFeature = (feature) => countryByCode.get(codeForFeature(feature));
	const meta = (metric) => capacity.metric_metadata[metric];
	const summary = (metric) => capacity.summary[metric];
	const valueFor = (country, metric) => country?.metrics?.[metric]?.value;
	const observationFor = (country, metric) => country?.metrics?.[metric];
	const formatValue = (value, metric) => {
		if (value === null || value === undefined) return 'No WHO observation';
		if (metric === 'government_mental_health_spending_share') return `${Number(value).toFixed(2)}%`;
		return `${Number(value).toFixed(value >= 10 ? 1 : 2)} per 100k`;
	};
	const binFor = (value, metric) => {
		if (value === null || value === undefined) return 'missing';
		const s = summary(metric);
		if (value <= s.q25) return 'q1';
		if (value <= s.median) return 'q2';
		if (value <= s.q75) return 'q3';
		return 'q4';
	};

	let selectedMeta = $derived(meta(selectedMetric));
	let selectedSummary = $derived(summary(selectedMetric));
	let coveragePct = $derived(Math.round((selectedSummary.n / capacity.country_area_universe) * 100));
	let regionRows = $derived(capacity.region_summaries
		.map((row) => ({ ...row, metric: row.metrics[selectedMetric] }))
		.filter((row) => row.metric?.n)
		.sort((a, b) => (b.metric.median ?? -Infinity) - (a.metric.median ?? -Infinity)));

	const mismatch = capacity.historical_mismatch_lens;
	const mismatchPairs = mismatch.pairs;
	const xMax = Math.max(...mismatchPairs.map((row) => row.capacity_value));
	const yValues = mismatchPairs.map((row) => row.depression_prevalence);
	const yMin = Math.min(...yValues);
	const yMax = Math.max(...yValues);
	const xScale = scaleSymlog().constant(0.5).domain([0, xMax]).range([58, 914]);
	const yScale = scaleLinear().domain([yMin - 0.15, yMax + 0.15]).range([390, 34]);
	const mismatchCount = mismatchPairs.filter((row) => row.quadrant === 'higher_depression_lower_capacity').length;
</script>

<svelte:head>
	<title>Global Mental Health Capacity Atlas · pudding-skill</title>
	<meta
		name="description"
		content="Explore WHO country-level mental-health workforce, spending and service-capacity indicators with reporting years and missingness kept visible."
	/>
</svelte:head>

<article class="atlas-shell">
	<header class="atlas-hero">
		<a class="back-link" href="/stories/global-mental-health">← Return to the field story</a>
		<p class="kicker">GLOBAL MENTAL HEALTH · CAPACITY ATLAS</p>
		<h1>Where does the system have <em>room to respond?</em></h1>
		<p class="dek">
			A country map of reported mental-health capacity from WHO's Global Health Observatory. The data are not a
			league table: countries report in different years, coverage varies by indicator, and missing never means zero.
		</p>
	</header>

	<section class="map-section" aria-labelledby="map-title">
		<div class="section-head">
			<div>
				<p class="eyebrow">CHOOSE A CAPACITY LENS</p>
				<h2 id="map-title">{selectedMeta.label}</h2>
				<p>
					{selectedSummary.n} of {capacity.country_area_universe} WHO country/area entries have a usable observation
					for this indicator ({coveragePct}% coverage). Observation years span {selectedSummary.year_min}–{selectedSummary.year_max}.
				</p>
			</div>
			<div class="coverage-card">
				<strong>{coveragePct}%</strong>
				<span>country/area coverage</span>
			</div>
		</div>

		<div class="metric-controls" aria-label="Choose mental-health capacity indicator">
			{#each metricOptions as metric}
				<button
					type="button"
					class:active={selectedMetric === metric}
					aria-pressed={selectedMetric === metric}
					onclick={() => (selectedMetric = metric)}
				>
					{meta(metric).label}
				</button>
			{/each}
		</div>

		<div class="map-frame">
			<svg class="world-map" viewBox="0 0 960 480" role="img" aria-labelledby="world-map-title world-map-desc">
				<title id="world-map-title">World map of {selectedMeta.label}</title>
				<desc id="world-map-desc">
					WHO observations by country. Darker categories indicate higher reported values. Gray countries have no usable observation.
				</desc>
				{#each world.features as feature}
					{@const country = countryForFeature(feature)}
					{@const observation = observationFor(country, selectedMetric)}
					{@const value = observation?.value}
					<path
						d={path(feature)}
						class={`country ${binFor(value, selectedMetric)}`}
						aria-label={`${country?.name || feature.properties?.name || 'Unknown'}: ${formatValue(value, selectedMetric)}${observation?.year ? `, ${observation.year}` : ''}`}
					>
						<title>{country?.name || feature.properties?.name || 'Unknown'} — {formatValue(value, selectedMetric)}{observation?.year ? ` · ${observation.year}` : ''}</title>
					</path>
				{/each}
			</svg>
			<div class="legend" aria-label="Map quartile legend">
				<span><i class="missing"></i>No observation</span>
				<span><i class="q1"></i>≤ Q1 {selectedSummary.q25}</span>
				<span><i class="q2"></i>Q1–median</span>
				<span><i class="q3"></i>median–Q3</span>
				<span><i class="q4"></i>&gt; Q3 {selectedSummary.q75}</span>
			</div>
		</div>

		<p class="map-note">
			Median among countries with an observation: <strong>{selectedSummary.median}</strong> {selectedMeta.unit}. The
			map bins only the countries that reported this indicator; it does not infer missing values.
		</p>
	</section>

	<section class="regions" aria-labelledby="regions-title">
		<div class="section-head compact">
			<div>
				<p class="eyebrow">REGIONAL CONTEXT</p>
				<h2 id="regions-title">The middle of the distribution changes by WHO region.</h2>
				<p>These are medians among countries with usable observations, not population-weighted regional averages.</p>
			</div>
		</div>
		<div class="region-list">
			{#each regionRows as row}
				<div class="region-row">
					<div>
						<strong>{row.region}</strong>
						<span>{row.metric.n} reporting countries/areas · median year {row.metric.year_median}</span>
					</div>
					<b>{row.metric.median}</b>
					<small>{selectedMeta.unit}</small>
				</div>
			{/each}
		</div>
	</section>

	<section class="mismatch" aria-labelledby="mismatch-title">
		<div class="mismatch-copy">
			<p class="eyebrow">HISTORICAL NEED × CAPACITY LENS</p>
			<h2 id="mismatch-title">A useful warning signal — not a current country score.</h2>
			<p>
				WHO's 2015 modeled depression-prevalence estimate can be paired with the latest available psychiatrist density
				for {mismatch.overlap_n} countries. {mismatchCount} sit above the sample median for depression prevalence and
				below the median for psychiatrist density. That quadrant is worth investigating, but the two axes describe
				different years and different constructs.
			</p>
		</div>

		<div class="scatter-frame">
			<svg class="scatter" viewBox="0 0 960 430" role="img" aria-labelledby="scatter-title scatter-desc">
				<title id="scatter-title">Historical depression prevalence and psychiatrist density</title>
				<desc id="scatter-desc">
					A descriptive scatter plot pairing 2015 modeled depression prevalence with each country's latest available psychiatrist-density observation.
				</desc>
				<line class="median-line" x1={xScale(mismatch.capacity_median)} x2={xScale(mismatch.capacity_median)} y1="24" y2="398" />
				<line class="median-line" x1="48" x2="924" y1={yScale(mismatch.need_median)} y2={yScale(mismatch.need_median)} />
				{#each mismatchPairs as row}
					<circle
						cx={xScale(row.capacity_value)}
						cy={yScale(row.depression_prevalence)}
						r={row.quadrant === 'higher_depression_lower_capacity' ? 4.5 : 3.2}
						class:priority={row.quadrant === 'higher_depression_lower_capacity'}
						aria-label={`${row.name}: depression prevalence ${row.depression_prevalence}% in ${row.depression_year}; psychiatrists ${row.capacity_value} per 100,000 in ${row.capacity_year}`}
					>
						<title>{row.name} — depression {row.depression_prevalence}% ({row.depression_year}); psychiatrists {row.capacity_value}/100k ({row.capacity_year})</title>
					</circle>
				{/each}
				<text class="axis-label" x="480" y="423" text-anchor="middle">Psychiatrists per 100,000 · latest WHO observation</text>
				<text class="axis-label vertical" transform="translate(16 215) rotate(-90)" text-anchor="middle">Depression prevalence · WHO 2015 estimate</text>
				<text class="quadrant-label" x="66" y="48">higher depression / lower psychiatrist density</text>
			</svg>
		</div>
		<div class="warning-box">
			<strong>Descriptive only.</strong>
			<p>{mismatch.caveat}</p>
		</div>
	</section>

	<section class="missingness" aria-labelledby="missing-title">
		<p class="eyebrow">THE BLANKS ARE DATA TOO</p>
		<h2 id="missing-title">Coverage itself tells us where comparison is fragile.</h2>
		<div class="coverage-grid">
			{#each metricOptions as metric}
				<article>
					<strong>{summary(metric).n}</strong>
					<span>of {capacity.country_area_universe}</span>
					<h3>{meta(metric).label}</h3>
					<p>Median reporting year: {summary(metric).year_median ?? 'n/a'}</p>
				</article>
			{/each}
		</div>
	</section>

	<footer class="atlas-footer">
		<div>
			<strong>{capacity.status}</strong>
			<p>Source: WHO Global Health Observatory. Country values preserve their reporting year. Natural Earth public-domain geometry is used only for geographic shapes.</p>
		</div>
		<a href="/stories/global-mental-health">Continue the main story →</a>
	</footer>
</article>

<style>
	.atlas-shell { --ink:#171715; --muted:#68645d; --paper:#f5f0e7; --card:#fffaf2; --accent:#a33f32; --line:#d7cfc2; color:var(--ink); background:var(--paper); min-height:100vh; }
	.atlas-hero,.map-section,.regions,.mismatch,.missingness,.atlas-footer { max-width:1180px; margin-inline:auto; padding-inline:clamp(1rem,5vw,5rem); }
	.atlas-hero { padding-top:clamp(4rem,8vw,8rem); padding-bottom:6rem; }
	.back-link { display:inline-flex; min-height:44px; align-items:center; color:var(--muted); font:700 .82rem/1.2 var(--font-sans); }
	.kicker,.eyebrow { font:800 .76rem/1.2 var(--font-sans); letter-spacing:.14em; color:var(--accent); }
	h1,h2,h3 { font-family:var(--font-serif); }
	h1 { max-width:1050px; margin:1rem 0 1.5rem; font-size:clamp(3.8rem,9.5vw,8.5rem); line-height:.9; letter-spacing:-.06em; }
	h1 em { color:var(--accent); font-weight:400; }
	.dek { max-width:780px; margin:0; color:var(--muted); font-size:clamp(1.1rem,2vw,1.45rem); line-height:1.6; }
	.map-section,.regions,.mismatch,.missingness { padding-top:6rem; padding-bottom:6rem; border-top:1px solid var(--line); }
	.section-head { display:grid; grid-template-columns:1fr auto; gap:3rem; align-items:end; }
	.section-head.compact { grid-template-columns:1fr; }
	.section-head h2,.mismatch h2,.missingness h2 { max-width:850px; margin:.7rem 0 1rem; font-size:clamp(2.5rem,5vw,5.2rem); line-height:.96; letter-spacing:-.04em; }
	.section-head p,.mismatch-copy > p:last-child { max-width:720px; color:var(--muted); line-height:1.65; }
	.coverage-card { min-width:160px; padding:1.2rem; border:1px solid var(--line); background:var(--card); }
	.coverage-card strong { display:block; font:800 3rem/.9 var(--font-sans); color:var(--accent); }
	.coverage-card span { display:block; margin-top:.6rem; color:var(--muted); font:700 .72rem/1.2 var(--font-sans); text-transform:uppercase; letter-spacing:.08em; }
	.metric-controls { display:flex; gap:.55rem; flex-wrap:wrap; margin:2.5rem 0 1.3rem; }
	.metric-controls button { min-height:44px; border:1px solid var(--line); border-radius:999px; padding:.65rem 1rem; background:transparent; color:var(--ink); font:700 .8rem/1.2 var(--font-sans); cursor:pointer; }
	.metric-controls button.active { background:var(--ink); border-color:var(--ink); color:var(--paper); }
	.map-frame { border:1px solid var(--line); background:#ebe5da; padding:clamp(.6rem,2vw,1.2rem); }
	.world-map { width:100%; height:auto; display:block; }
	.country { stroke:#f5f0e7; stroke-width:.55; vector-effect:non-scaling-stroke; }
	.country.missing { fill:#d5d0c7; }
	.country.q1 { fill:#dcc5bd; }
	.country.q2 { fill:#c99080; }
	.country.q3 { fill:#a85d4d; }
	.country.q4 { fill:#6f2d24; }
	.legend { display:flex; flex-wrap:wrap; gap:.8rem 1.2rem; padding:.8rem .4rem .2rem; color:var(--muted); font:650 .72rem/1.2 var(--font-sans); }
	.legend span { display:flex; align-items:center; gap:.4rem; }
	.legend i { width:12px; height:12px; display:inline-block; border:1px solid rgba(0,0,0,.08); }
	.legend .missing { background:#d5d0c7; } .legend .q1{background:#dcc5bd;} .legend .q2{background:#c99080;} .legend .q3{background:#a85d4d;} .legend .q4{background:#6f2d24;}
	.map-note { max-width:800px; margin:1.2rem 0 0; color:var(--muted); line-height:1.6; }
	.region-list { margin-top:3rem; border-top:1px solid var(--line); }
	.region-row { display:grid; grid-template-columns:1fr auto 150px; gap:1rem; align-items:center; padding:1.1rem 0; border-bottom:1px solid var(--line); }
	.region-row div { display:grid; gap:.2rem; }
	.region-row div strong { font:700 1.05rem/1.2 var(--font-sans); }
	.region-row div span,.region-row small { color:var(--muted); font:600 .75rem/1.35 var(--font-sans); }
	.region-row b { color:var(--accent); font:800 1.5rem/1 var(--font-sans); }
	.mismatch { background:#1d211f; color:#f7f3eb; max-width:none; padding-inline:max(clamp(1rem,5vw,5rem), calc((100vw - 1180px)/2 + clamp(1rem,5vw,5rem))); }
	.mismatch-copy { max-width:1180px; margin:auto; }
	.mismatch .eyebrow { color:#f0b6a9; }
	.mismatch-copy > p:last-child { color:#c6c9c2; }
	.scatter-frame { max-width:1180px; margin:3rem auto 0; border:1px solid #3b433f; background:#171a18; padding:.75rem; }
	.scatter { width:100%; height:auto; display:block; overflow:visible; }
	.scatter circle { fill:#89958e; opacity:.55; stroke:none; }
	.scatter circle.priority { fill:#ef9b87; opacity:.9; }
	.median-line { stroke:#68736d; stroke-width:1; stroke-dasharray:5 6; }
	.axis-label,.quadrant-label { fill:#9fa8a3; font:650 12px/1 var(--font-sans); }
	.quadrant-label { fill:#ef9b87; font-weight:800; letter-spacing:.04em; text-transform:uppercase; }
	.warning-box { max-width:760px; margin:1.2rem auto 0; padding:1rem 1.2rem; border-left:3px solid #ef9b87; background:#242a27; }
	.warning-box strong { color:#f0b6a9; font:800 .78rem/1.2 var(--font-sans); text-transform:uppercase; letter-spacing:.08em; }
	.warning-box p { margin:.4rem 0 0; color:#c6c9c2; line-height:1.55; }
	.coverage-grid { display:grid; grid-template-columns:repeat(5,1fr); gap:1px; margin-top:3rem; background:var(--line); border:1px solid var(--line); }
	.coverage-grid article { padding:1.2rem; background:var(--card); }
	.coverage-grid strong { font:800 2.4rem/1 var(--font-sans); color:var(--accent); }
	.coverage-grid span { color:var(--muted); font:650 .75rem/1.2 var(--font-sans); }
	.coverage-grid h3 { margin:1rem 0 .5rem; font-size:1.05rem; }
	.coverage-grid p { margin:0; color:var(--muted); font:600 .75rem/1.4 var(--font-sans); }
	.atlas-footer { padding-top:2rem; padding-bottom:5rem; border-top:1px solid var(--line); display:flex; justify-content:space-between; gap:2rem; align-items:flex-start; }
	.atlas-footer strong { color:var(--accent); font:800 .75rem/1.2 var(--font-sans); letter-spacing:.06em; }
	.atlas-footer p { max-width:720px; color:var(--muted); font:600 .78rem/1.5 var(--font-sans); }
	.atlas-footer a { min-height:44px; display:inline-flex; align-items:center; color:var(--ink); font:800 .82rem/1.2 var(--font-sans); white-space:nowrap; }
	@media (max-width:820px) {
		.section-head { grid-template-columns:1fr; gap:1.2rem; }
		.coverage-card { width:fit-content; }
		.map-frame { margin-inline:-.4rem; }
		.region-row { grid-template-columns:1fr auto; }
		.region-row small { grid-column:1 / -1; }
		.coverage-grid { grid-template-columns:1fr 1fr; }
		.mismatch { padding-inline:clamp(1rem,5vw,5rem); }
	}
	@media (max-width:520px) {
		.atlas-hero { padding-bottom:4rem; }
		.metric-controls { display:grid; grid-template-columns:1fr; }
		.metric-controls button { border-radius:8px; text-align:left; }
		.legend { display:grid; grid-template-columns:1fr 1fr; }
		.coverage-grid { grid-template-columns:1fr; }
		.atlas-footer { flex-direction:column; }
		.quadrant-label { font-size:10px; }
	}
</style>
