<script>
	import { base } from '$app/paths';
	import { onMount } from 'svelte';
	import facts from '$data/global-mental-health-facts.json';

	const fact = (id) => facts.facts.find((row) => row.id === id);
	const number = (id) => Number(String(fact(id)?.value || '').replace(/[^0-9.]/g, ''));

	let focus = $state('');
	onMount(() => {
		focus = (new URL(window.location.href).searchParams.get('focus') || '').toUpperCase();
	});
	const show = (alias) => !focus || focus === alias;

	const lowSpend = number('mental-health-spend-lic');
	const highSpend = number('mental-health-spend-hic');
	const spendRatio = Math.round(highSpend / lowSpend);
	const globalShare = fact('mental-health-spending');
	const prevalence = fact('global-prevalence-2021');

	const guidedStates = [
		{
			label: '1 · Need',
			value: prevalence.value,
			copy: 'people were living with a mental disorder in 2021. The need is global before resources are compared.'
		},
		{
			label: '2 · Public priority',
			value: globalShare.value,
			copy: 'is the global median share of government health expenditure allocated to mental health among reporting countries.'
		},
		{
			label: '3 · Capacity gap',
			value: `${spendRatio.toLocaleString()}×`,
			copy: `is the approximate gap between the Atlas 2024 income-group medians: $${lowSpend.toFixed(2)} per person in low-income countries versus $${highSpend.toFixed(2)} in high-income countries.`
		}
	];
	let guidedStep = $state(2);

	const explorerMetrics = [
		{
			id: 'spend',
			label: 'Government mental-health spending per person',
			low: lowSpend,
			high: highSpend,
			unit: '$',
			note: 'Atlas 2024 income-group medians among reporting countries.'
		},
		{
			id: 'service',
			label: 'Modeled MDD mental-health service use',
			low: number('mdd-service-low'),
			high: number('mdd-service-hic'),
			unit: '%',
			note: 'Systematic review/meta-regression; evidence in low-resource settings was sparse.'
		},
		{
			id: 'adequate',
			label: 'Modeled minimally adequate MDD treatment',
			low: number('mdd-mat-low'),
			high: number('mdd-mat-hic'),
			unit: '%',
			note: 'Modeled estimates with wide uncertainty intervals; use as comparison, not ranking.'
		}
	];
	let selectedMetricId = $state('spend');
	const selectedMetric = $derived(explorerMetrics.find((row) => row.id === selectedMetricId) || explorerMetrics[0]);
	const maxMetric = $derived(Math.max(selectedMetric.low, selectedMetric.high));
	const formatMetric = (value, unit) => (unit === '$' ? `$${value.toFixed(2)}` : `${value}%`);
</script>

<svelte:head>
	<title>Prototype tournament · Global mental health · pudding-skill</title>
	<meta
		name="description"
		content="Low-cost visual prototypes for comparing static, guided, and explorable global mental-health story concepts before production implementation."
	/>
</svelte:head>

<div class="tournament-page" class:focused={Boolean(focus)}>
	<header class="intro">
		<a class="back" href={`${base}/stories/global-mental-health`}>← Back to story</a>
		<p class="eyebrow">PROTOTYPE TOURNAMENT · LOW-FIDELITY ON PURPOSE</p>
		<h1>Three ways to show the same care-capacity gap.</h1>
		<p class="dek">
			These are not finished designs. Each direction implements only its hardest claim-bearing moment so the editorial form can be judged before bespoke code becomes sunk cost.
		</p>
	</header>

	<section class="prototype-grid" aria-label="Prototype comparison">
		{#if show('A')}
			<article class="prototype" data-prototype-alias="A" id="prototype-a">
				<div class="prototype-head">
					<span class="alias">A</span>
					<div>
						<p>STATIC · NO INTERACTION</p>
						<h2>A gap that fits on one screen</h2>
					</div>
				</div>

				<div class="static-hero">
					<strong>{spendRatio.toLocaleString()}×</strong>
					<p>approximate difference between the reported income-group medians for government mental-health spending per person.</p>
				</div>

				<div class="bars" role="img" aria-label={`Low-income median $${lowSpend.toFixed(2)} per person; high-income median $${highSpend.toFixed(2)} per person.`}>
					<div class="bar-row">
						<div class="bar-label"><span>Low income</span><strong>${lowSpend.toFixed(2)}</strong></div>
						<div class="track"><i style={`width: ${Math.max(1.5, (lowSpend / highSpend) * 100)}%`}></i></div>
					</div>
					<div class="bar-row">
						<div class="bar-label"><span>High income</span><strong>${highSpend.toFixed(2)}</strong></div>
						<div class="track"><i style="width: 100%"></i></div>
					</div>
				</div>

				<p class="caveat">WHO Mental Health Atlas 2024 · income-group medians among reporting countries. This is not a country ranking and does not imply equal reporting coverage.</p>
			</article>
		{/if}

		{#if show('B')}
			<article class="prototype" data-prototype-alias="B" id="prototype-b">
				<div class="prototype-head">
					<span class="alias">B</span>
					<div>
						<p>GUIDED · REVEAL</p>
						<h2>Need → priority → capacity</h2>
					</div>
				</div>

				<div class="step-tabs" role="group" aria-label="Choose guided prototype step">
					{#each guidedStates as state, index}
						<button class:active={guidedStep === index} type="button" onclick={() => (guidedStep = index)}>
							{state.label}
						</button>
					{/each}
				</div>

				<div class="guided-stage" aria-live="polite">
					<div class="ladder" aria-hidden="true">
						{#each guidedStates as _, index}
							<i class:reached={index <= guidedStep}></i>
						{/each}
					</div>
					<p class="stage-label">{guidedStates[guidedStep].label}</p>
					<strong>{guidedStates[guidedStep].value}</strong>
					<p>{guidedStates[guidedStep].copy}</p>
				</div>

				<p class="caveat">The reveal earns its place only if preserving one frame helps readers understand why each resource layer changes the argument. Reduced motion loses no evidence.</p>
			</article>
		{/if}

		{#if show('C')}
			<article class="prototype" data-prototype-alias="C" id="prototype-c">
				<div class="prototype-head">
					<span class="alias">C</span>
					<div>
						<p>EXPLORABLE · COMPARE</p>
						<h2>Let the reader change the capacity lens</h2>
					</div>
				</div>

				<label class="metric-control">
					<span>Comparison metric</span>
					<select bind:value={selectedMetricId}>
						{#each explorerMetrics as metric}
							<option value={metric.id}>{metric.label}</option>
						{/each}
					</select>
				</label>

				<div class="compare-pair" aria-live="polite">
					<div>
						<span>Low / lower-resource group</span>
						<strong>{formatMetric(selectedMetric.low, selectedMetric.unit)}</strong>
						<i style={`width: ${Math.max(3, (selectedMetric.low / maxMetric) * 100)}%`}></i>
					</div>
					<div>
						<span>High-income group</span>
						<strong>{formatMetric(selectedMetric.high, selectedMetric.unit)}</strong>
						<i style={`width: ${(selectedMetric.high / maxMetric) * 100}%`}></i>
					</div>
				</div>

				<p class="metric-note">{selectedMetric.note}</p>
				<p class="caveat">Exploration is justified only if changing the metric teaches that “capacity” is multidimensional. The production version must keep year, denominator, uncertainty, and missingness visible.</p>
			</article>
		{/if}
	</section>

	<section class="judge-note">
		<p class="eyebrow">JUDGING RULE</p>
		<h2>Complexity gets no bonus.</h2>
		<p>
			All three directions are scored on reader realization, evidence fidelity, visual necessity, interaction economy, reader effort, mobile viability, and accessibility equivalence. A static prototype can win outright. Evidence, mobile, and accessibility failures are elimination gates.
		</p>
	</section>
</div>

<style>
	:global(body) {
		margin: 0;
		background: #f1eee7;
		color: #191917;
	}

	.tournament-page {
		--ink: #191917;
		--card: #fffdf8;
		--muted: #69655f;
		--line: #d6d0c5;
		--accent: #9d3d31;
		min-height: 100vh;
		padding: 2rem 20px 5rem;
	}

	.tournament-page.focused {
		min-height: auto;
		padding-top: 1rem;
		padding-bottom: 1rem;
	}

	.focused .intro,
	.focused .judge-note {
		display: none;
	}

	.intro,
	.prototype-grid,
	.judge-note {
		width: min(1320px, 100%);
		margin-inline: auto;
	}

	.intro {
		padding: 1rem 0 3rem;
	}

	.back {
		display: inline-flex;
		align-items: center;
		min-height: 44px;
		color: var(--ink);
		font: 700 0.8rem/1 var(--font-sans);
		text-decoration: none;
	}

	.eyebrow,
	.prototype-head p,
	.stage-label {
		font: 800 0.72rem/1.2 var(--font-mono);
		letter-spacing: 0.1em;
		text-transform: uppercase;
		color: var(--accent);
	}

	h1,
	h2 {
		font-family: var(--font-serif);
	}

	h1 {
		max-width: 920px;
		margin: 2.5rem 0 1rem;
		font-size: clamp(2.7rem, 6vw, 5.8rem);
		line-height: 0.95;
	}

	.dek {
		max-width: 760px;
		font: 1.05rem/1.6 var(--font-sans);
		color: var(--muted);
	}

	.prototype-grid {
		display: grid;
		grid-template-columns: repeat(3, minmax(0, 1fr));
		gap: 1rem;
		align-items: stretch;
	}

	.focused .prototype-grid {
		grid-template-columns: minmax(0, 780px);
		justify-content: center;
	}

	.prototype {
		display: flex;
		min-width: 0;
		min-height: 720px;
		flex-direction: column;
		gap: 1.5rem;
		padding: clamp(1.2rem, 2vw, 2rem);
		border: 1px solid var(--line);
		border-radius: 20px;
		background: var(--card);
		box-shadow: 0 14px 36px rgb(25 25 23 / 0.06);
	}

	.prototype-head {
		display: grid;
		grid-template-columns: 46px 1fr;
		gap: 0.85rem;
		align-items: start;
	}

	.alias {
		display: grid;
		width: 46px;
		height: 46px;
		place-items: center;
		border-radius: 50%;
		background: var(--ink);
		color: white;
		font: 800 1rem/1 var(--font-mono);
	}

	.prototype-head p {
		margin: 0.2rem 0 0.45rem;
	}

	.prototype-head h2 {
		margin: 0;
		font-size: clamp(1.55rem, 2.3vw, 2.25rem);
		line-height: 1.05;
	}

	.static-hero {
		padding: 1.2rem 0 0.5rem;
	}

	.static-hero strong,
	.guided-stage > strong {
		display: block;
		font: 650 clamp(4rem, 8vw, 6.8rem)/0.9 var(--font-serif);
		letter-spacing: -0.05em;
	}

	.static-hero p,
	.guided-stage > p,
	.metric-note,
	.caveat,
	.judge-note > p {
		font: 0.95rem/1.55 var(--font-sans);
	}

	.static-hero p {
		max-width: 36ch;
		margin: 0.8rem 0 0;
		color: var(--muted);
	}

	.bars,
	.compare-pair {
		display: grid;
		gap: 1.2rem;
	}

	.bar-label {
		display: flex;
		justify-content: space-between;
		gap: 1rem;
		margin-bottom: 0.5rem;
		font: 0.9rem/1.2 var(--font-sans);
	}

	.track {
		height: 18px;
		overflow: hidden;
		border-radius: 999px;
		background: #e6e0d6;
	}

	.track i,
	.compare-pair i {
		display: block;
		height: 100%;
		min-width: 3px;
		border-radius: inherit;
		background: var(--accent);
	}

	.caveat {
		margin-top: auto;
		padding-top: 1rem;
		border-top: 1px solid var(--line);
		color: var(--muted);
	}

	.step-tabs {
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		gap: 0.4rem;
	}

	.step-tabs button {
		min-height: 48px;
		padding: 0.65rem;
		border: 1px solid var(--line);
		border-radius: 10px;
		background: transparent;
		color: var(--ink);
		font: 700 0.78rem/1.2 var(--font-sans);
		cursor: pointer;
	}

	.step-tabs button.active {
		border-color: var(--ink);
		background: var(--ink);
		color: white;
	}

	.guided-stage {
		padding: clamp(1.2rem, 3vw, 2rem);
		border-radius: 16px;
		background: #f3eadf;
	}

	.ladder {
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		gap: 0.35rem;
		margin-bottom: 2rem;
	}

	.ladder i {
		height: 8px;
		border-radius: 99px;
		background: #d6cfc5;
	}

	.ladder i.reached {
		background: var(--accent);
	}

	.guided-stage .stage-label {
		margin: 0 0 0.55rem;
	}

	.guided-stage > p:last-child {
		max-width: 42ch;
		margin-bottom: 0;
		color: var(--muted);
	}

	.metric-control {
		display: grid;
		gap: 0.5rem;
		font: 700 0.8rem/1.2 var(--font-sans);
	}

	.metric-control select {
		width: 100%;
		min-height: 48px;
		padding: 0.65rem 2.2rem 0.65rem 0.75rem;
		border: 1px solid var(--ink);
		border-radius: 10px;
		background: white;
		color: var(--ink);
		font: 0.9rem/1.2 var(--font-sans);
	}

	.compare-pair > div {
		display: grid;
		grid-template-columns: 1fr auto;
		gap: 0.5rem 1rem;
		align-items: end;
	}

	.compare-pair span {
		font: 0.82rem/1.3 var(--font-sans);
		color: var(--muted);
	}

	.compare-pair strong {
		font: 650 1.8rem/1 var(--font-serif);
	}

	.compare-pair i {
		grid-column: 1 / -1;
		height: 14px;
	}

	.metric-note {
		margin: 0;
		color: var(--muted);
	}

	.judge-note {
		padding: 5rem 0 1rem;
	}

	.judge-note h2 {
		max-width: 720px;
		margin: 0.5rem 0 1rem;
		font-size: clamp(2.2rem, 4vw, 4rem);
	}

	.judge-note > p:last-child {
		max-width: 760px;
		color: var(--muted);
	}

	@media (max-width: 980px) {
		.prototype-grid {
			grid-template-columns: 1fr;
		}

		.prototype {
			min-height: 0;
		}
	}

	@media (max-width: 560px) {
		.tournament-page {
			padding-inline: 14px;
		}

		.tournament-page.focused {
			padding-top: 0.5rem;
		}

		.intro {
			padding-bottom: 2rem;
		}

		h1 {
			margin-top: 1.8rem;
			font-size: clamp(2.6rem, 14vw, 4rem);
		}

		.prototype {
			gap: 1rem;
			padding: 1rem;
			border-radius: 14px;
		}

		.prototype-head {
			grid-template-columns: 40px 1fr;
		}

		.alias {
			width: 40px;
			height: 40px;
		}

		.step-tabs {
			grid-template-columns: repeat(3, 1fr);
		}

		.step-tabs button {
			padding-inline: 0.3rem;
			font-size: 0.7rem;
		}

		.static-hero strong,
		.guided-stage > strong {
			font-size: clamp(3.7rem, 21vw, 5.7rem);
		}
	}

	@media (prefers-reduced-motion: reduce) {
		* {
			scroll-behavior: auto !important;
			transition: none !important;
		}
	}
</style>
