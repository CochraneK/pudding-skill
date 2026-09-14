<script>
	import { geoNaturalEarth1, geoPath } from 'd3';
	import capacity from '$data/global-mental-health-capacity.json';
	import worldRaw from '$data/world-110m.geojson?raw';
	import { language } from '$lib/language.js';

	const world = JSON.parse(worldRaw);
	const countryByCode = new Map(capacity.countries.map((country) => [country.code, country]));
	const metrics = [
		'psychiatrists_per_100k',
		'mental_health_nurses_per_100k',
		'psychologists_per_100k',
		'government_mental_health_spending_share'
	];

	let selectedMetric = $state('psychiatrists_per_100k');
	let hoveredCode = $state(null);
	let selectedCode = $state(null);

	const projection = geoNaturalEarth1().fitExtent(
		[
			[12, 12],
			[948, 468]
		],
		world
	);
	const path = geoPath(projection);

	const translations = {
		zh: {
			eyebrow: '现在交给你 · 自由探索',
			title: '故事讲完以后，地图不再替你做结论。',
			dek: '切换指标、指向或点击国家。颜色表示该指标在有数据国家中的四分位位置，而不是“好/坏”评分。灰色就是缺失，不会被偷偷填成 0。',
			coverage: '国家/地区有可用观测',
			years: '观测年份',
			missing: '无 WHO 可用观测',
			click: '点击国家可锁定；再次点击同一国家取消。',
			quartiles: ['较低四分位', '中低四分位', '中高四分位', '较高四分位'],
			metricLabels: {
				psychiatrists_per_100k: '精神科医生',
				mental_health_nurses_per_100k: '精神健康护士',
				psychologists_per_100k: '心理学家',
				government_mental_health_spending_share: '政府精神健康支出占比'
			},
			unitPer100k: '每 10 万人',
			unitShare: '政府卫生支出的 %',
			region: 'WHO 区域',
			year: '年份',
			value: '观测值',
			emptyTitle: '把鼠标移到一个国家上，或点击它。',
			emptyBody: '这里会显示数值和报告年份。先看年份，再比较数值。',
			caveat: '注意：不同指标来自不同 Atlas/GHO 轮次，不能当作 2026 年实时排名。'
		},
		en: {
			eyebrow: 'NOW IT IS YOUR TURN · EXPLORE',
			title: 'After the guided story, the map stops making the conclusion for you.',
			dek: 'Switch metrics, hover, or click a country. Color encodes quartile position among countries with observations — not a good/bad score. Gray means missing, never zero-filled.',
			coverage: 'countries/areas with usable observations',
			years: 'observation years',
			missing: 'No usable WHO observation',
			click: 'Click a country to pin it; click the same country again to clear.',
			quartiles: ['Lower quartile', 'Lower-middle quartile', 'Upper-middle quartile', 'Upper quartile'],
			metricLabels: {
				psychiatrists_per_100k: 'Psychiatrists',
				mental_health_nurses_per_100k: 'Mental-health nurses',
				psychologists_per_100k: 'Psychologists',
				government_mental_health_spending_share: 'Government mental-health spending share'
			},
			unitPer100k: 'per 100,000',
			unitShare: '% of government health expenditure',
			region: 'WHO region',
			year: 'Year',
			value: 'Observation',
			emptyTitle: 'Hover or click a country.',
			emptyBody: 'Its value and reporting year will appear here. Read the year before comparing the number.',
			caveat: 'Caution: indicators come from different Atlas/GHO rounds and are not a live 2026 ranking.'
		}
	};

	const t = () => translations[$language];
	const summary = (metric) => capacity.summary[metric];
	const codeForFeature = (feature) => {
		const props = feature.properties || {};
		const candidates = [props.code, props.iso_a3_eh, props.iso_a3];
		return candidates.find((code) => code && code !== '-99') || null;
	};
	const countryForFeature = (feature) => countryByCode.get(codeForFeature(feature));
	const observation = (country, metric) => country?.metrics?.[metric] || null;
	const value = (country, metric) => observation(country, metric)?.value;
	const binFor = (metricValue, metric) => {
		if (metricValue === null || metricValue === undefined) return 'missing';
		const s = summary(metric);
		if (metricValue <= s.q25) return 'q1';
		if (metricValue <= s.median) return 'q2';
		if (metricValue <= s.q75) return 'q3';
		return 'q4';
	};
	const formatValue = (metricValue, metric) => {
		if (metricValue === null || metricValue === undefined) return t().missing;
		if (metric === 'government_mental_health_spending_share') return `${Number(metricValue).toFixed(2)}%`;
		return `${Number(metricValue).toFixed(metricValue >= 10 ? 1 : 2)} ${t().unitPer100k}`;
	};
	const unitFor = (metric) => metric === 'government_mental_health_spending_share' ? t().unitShare : t().unitPer100k;

	let selectedSummary = $derived(summary(selectedMetric));
	let coveragePct = $derived(Math.round((selectedSummary.n / capacity.country_area_universe) * 100));
	let focusCode = $derived(selectedCode || hoveredCode);
	let focusCountry = $derived(focusCode ? countryByCode.get(focusCode) : null);
	let focusObservation = $derived(focusCountry ? observation(focusCountry, selectedMetric) : null);

	function chooseCountry(code) {
		if (!code) return;
		selectedCode = selectedCode === code ? null : code;
	}
</script>

<section class="explorer" aria-labelledby="capacity-explorer-title">
	<div class="explorer-head">
		<div>
			<p class="eyebrow">{t().eyebrow}</p>
			<h2 id="capacity-explorer-title">{t().title}</h2>
			<p>{t().dek}</p>
		</div>
		<div class="coverage">
			<strong>{coveragePct}%</strong>
			<span>{selectedSummary.n} / {capacity.country_area_universe} {t().coverage}</span>
			<small>{t().years}: {selectedSummary.year_min}–{selectedSummary.year_max}</small>
		</div>
	</div>

	<div class="controls" aria-label={$language === 'zh' ? '选择容量指标' : 'Choose capacity metric'}>
		{#each metrics as metric}
			<button
				type="button"
				class:active={selectedMetric === metric}
				aria-pressed={selectedMetric === metric}
				onclick={() => {
					selectedMetric = metric;
					selectedCode = null;
				}}
			>
				{t().metricLabels[metric]}
			</button>
		{/each}
	</div>

	<div class="explorer-grid">
		<div class="map-card">
			<div class="map-title">
				<h3>{t().metricLabels[selectedMetric]}</h3>
				<span>{unitFor(selectedMetric)}</span>
			</div>
			<svg class="world-map" viewBox="0 0 960 480" role="img" aria-label={`${t().metricLabels[selectedMetric]} world map`}>
				{#each world.features as feature}
					{@const country = countryForFeature(feature)}
					{@const code = codeForFeature(feature)}
					{@const metricValue = value(country, selectedMetric)}
					<path
						d={path(feature)}
						class={`country ${binFor(metricValue, selectedMetric)}`}
						class:focused={focusCode && focusCode === code}
						tabindex={country ? 0 : undefined}
						role={country ? 'button' : undefined}
						aria-label={country ? `${country.name}: ${formatValue(metricValue, selectedMetric)}` : undefined}
						onpointerenter={() => (hoveredCode = code)}
						onpointerleave={() => (hoveredCode = null)}
						onfocus={() => (hoveredCode = code)}
						onblur={() => (hoveredCode = null)}
						onclick={() => chooseCountry(code)}
						onkeydown={(event) => {
							if ((event.key === 'Enter' || event.key === ' ') && code) {
								event.preventDefault();
								chooseCountry(code);
							}
						}}
					></path>
				{/each}
			</svg>

			<div class="legend" aria-label={$language === 'zh' ? '四分位图例' : 'Quartile legend'}>
				{#each ['q1', 'q2', 'q3', 'q4'] as bin, i}
					<span><i class={bin}></i>{t().quartiles[i]}</span>
				{/each}
				<span><i class="missing"></i>{t().missing}</span>
			</div>
		</div>

		<aside class="country-card" aria-live="polite">
			{#if focusCountry}
				<p class="card-kicker">{selectedCode === focusCode ? ($language === 'zh' ? '已锁定' : 'PINNED') : ($language === 'zh' ? '当前国家' : 'CURRENT COUNTRY')}</p>
				<h3>{focusCountry.name}</h3>
				<div class="country-value">
					<strong>{formatValue(focusObservation?.value, selectedMetric)}</strong>
					<span>{t().metricLabels[selectedMetric]}</span>
				</div>
				<dl>
					<div><dt>{t().region}</dt><dd>{focusCountry.region}</dd></div>
					<div><dt>{t().year}</dt><dd>{focusObservation?.year ?? '—'}</dd></div>
					<div><dt>{t().value}</dt><dd>{focusObservation ? formatValue(focusObservation.value, selectedMetric) : t().missing}</dd></div>
				</dl>
			{:else}
				<p class="card-kicker">{ $language === 'zh' ? '探索提示' : 'EXPLORATION CUE' }</p>
				<h3>{t().emptyTitle}</h3>
				<p class="empty-copy">{t().emptyBody}</p>
			{/if}
			<p class="click-note">{t().click}</p>
			<p class="caveat">{t().caveat}</p>
		</aside>
	</div>
</section>

<style>
	.explorer {
		--ink: #171715;
		--paper: #f5f0e7;
		--panel: #fffaf2;
		--muted: #68645d;
		--accent: #a33f32;
		--line: #d7cfc2;
		max-width: 1240px;
		margin: 0 auto;
		padding: clamp(6rem, 10vw, 10rem) clamp(1rem, 4vw, 3rem);
	}
	.explorer-head { display: grid; grid-template-columns: 1.25fr 0.55fr; gap: 4rem; align-items: end; }
	.eyebrow, .card-kicker { margin: 0 0 0.8rem; font: 800 0.72rem/1.2 var(--font-mono); letter-spacing: 0.1em; color: var(--accent); }
	.explorer-head h2 { max-width: 850px; margin: 0; font: 600 clamp(2.8rem, 6vw, 6rem)/0.94 var(--font-serif); letter-spacing: -0.05em; }
	.explorer-head > div:first-child > p:last-child { max-width: 72ch; margin: 1.3rem 0 0; color: var(--muted); font: 500 1.04rem/1.65 var(--font-sans); }
	.coverage { padding: 1.3rem 0 0 1.4rem; border-left: 3px solid var(--accent); }
	.coverage strong, .coverage span, .coverage small { display: block; }
	.coverage strong { font: 800 clamp(3.4rem, 6vw, 5.5rem)/0.9 var(--font-sans); letter-spacing: -0.06em; color: var(--accent); }
	.coverage span { margin-top: 0.7rem; font: 700 0.82rem/1.35 var(--font-sans); }
	.coverage small { margin-top: 0.45rem; color: var(--muted); font: 500 0.75rem/1.35 var(--font-sans); }

	.controls { display: flex; flex-wrap: wrap; gap: 0.5rem; margin: 3rem 0 1rem; }
	.controls button { min-height: 44px; padding: 0.7rem 0.9rem; border: 1px solid var(--ink); background: transparent; color: var(--ink); font: 700 0.8rem/1.2 var(--font-sans); cursor: pointer; }
	.controls button.active { background: var(--ink); color: var(--paper); }
	.controls button:focus-visible { outline: 3px solid var(--accent); outline-offset: 2px; }

	.explorer-grid { display: grid; grid-template-columns: minmax(0, 1fr) minmax(260px, 0.32fr); gap: 1rem; align-items: stretch; }
	.map-card, .country-card { border: 1px solid var(--line); background: var(--panel); }
	.map-card { padding: clamp(0.75rem, 2vw, 1.4rem); overflow: hidden; }
	.map-title { display: flex; justify-content: space-between; gap: 1rem; align-items: baseline; }
	.map-title h3 { margin: 0; font: 600 clamp(1.5rem, 2.5vw, 2.4rem)/1 var(--font-serif); }
	.map-title span { color: var(--muted); font: 600 0.75rem/1.2 var(--font-sans); }
	.world-map { display: block; width: 100%; height: auto; margin-top: 1rem; }
	.country { stroke: #f5f0e7; stroke-width: 0.55; vector-effect: non-scaling-stroke; cursor: pointer; transition: opacity 120ms ease, stroke-width 120ms ease; }
	.country.q1 { fill: #e8c7bd; }
	.country.q2 { fill: #d99a89; }
	.country.q3 { fill: #bd6654; }
	.country.q4 { fill: #82392f; }
	.country.missing { fill: #d8d4cc; cursor: default; }
	.country:hover, .country:focus-visible, .country.focused { stroke: #171715; stroke-width: 1.5; outline: none; }
	.legend { display: flex; flex-wrap: wrap; gap: 0.65rem 1rem; padding-top: 0.7rem; border-top: 1px solid var(--line); color: var(--muted); font: 550 0.68rem/1.3 var(--font-sans); }
	.legend span { display: inline-flex; align-items: center; gap: 0.35rem; }
	.legend i { width: 12px; height: 12px; border-radius: 2px; }
	.legend i.q1 { background: #e8c7bd; } .legend i.q2 { background: #d99a89; } .legend i.q3 { background: #bd6654; } .legend i.q4 { background: #82392f; } .legend i.missing { background: #d8d4cc; }

	.country-card { padding: clamp(1.2rem, 2.5vw, 2rem); display: flex; flex-direction: column; min-height: 100%; }
	.country-card h3 { margin: 0 0 1.5rem; font: 600 clamp(2rem, 4vw, 3.8rem)/0.95 var(--font-serif); letter-spacing: -0.04em; }
	.country-value { padding: 1.2rem 0; border-top: 1px solid var(--line); border-bottom: 1px solid var(--line); }
	.country-value strong, .country-value span { display: block; }
	.country-value strong { font: 800 clamp(2.2rem, 4vw, 4rem)/0.95 var(--font-sans); letter-spacing: -0.05em; color: var(--accent); }
	.country-value span { margin-top: 0.6rem; color: var(--muted); font: 650 0.78rem/1.35 var(--font-sans); }
	dl { margin: 1rem 0 0; }
	dl div { display: grid; grid-template-columns: 0.72fr 1fr; gap: 0.8rem; padding: 0.7rem 0; border-bottom: 1px solid var(--line); }
	dt, dd { margin: 0; font: 600 0.75rem/1.35 var(--font-sans); }
	dt { color: var(--muted); } dd { text-align: right; }
	.empty-copy, .click-note, .caveat { color: var(--muted); font: 500 0.82rem/1.55 var(--font-sans); }
	.click-note { margin-top: auto; padding-top: 1.2rem; }
	.caveat { padding-top: 1rem; border-top: 1px solid var(--line); }

	@media (max-width: 820px) {
		.explorer-head, .explorer-grid { grid-template-columns: 1fr; }
		.explorer-head { gap: 2rem; }
		.coverage { border-left: 0; border-top: 3px solid var(--accent); padding-left: 0; }
		.map-title { flex-direction: column; gap: 0.35rem; }
		.country-card { min-height: 320px; }
	}

	@media (prefers-reduced-motion: reduce) {
		.country { transition: none; }
	}
</style>
