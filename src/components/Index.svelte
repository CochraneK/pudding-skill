<script>
	import { onMount } from "svelte";
	import Footer from "$components/Footer.svelte";

	let active = $state(0);

	const labels = ["Harbor", "Summit", "Cedar", "Mesa"];
	const states = [
		{
			title: "Start with a baseline",
			note: "All four fictional cities begin at the same 2019 index.",
			values: [32, 32, 32, 32]
		},
		{
			title: "Reveal the divergence",
			note: "Housing pressure rises faster in Harbor and Summit.",
			values: [74, 66, 45, 41]
		},
		{
			title: "Compare, do not decorate",
			note: "The visual state exists to support a comparison, not to create motion for its own sake.",
			values: [74, 66, 45, 41]
		},
		{
			title: "End with the caveat",
			note: "This demo uses synthetic values. A real story must keep evidence, source and claim aligned.",
			values: [74, 66, 45, 41]
		}
	];

	onMount(() => {
		const nodes = Array.from(document.querySelectorAll("[data-story-step]"));
		const observer = new IntersectionObserver(
			(entries) => {
				for (const entry of entries) {
					if (entry.isIntersecting) active = Number(entry.target.dataset.storyStep || 0);
				}
			},
			{ rootMargin: "-35% 0px -45% 0px", threshold: 0.05 }
		);

		nodes.forEach((node) => observer.observe(node));
		return () => observer.disconnect();
	});
</script>

<svelte:head>
	<meta name="theme-color" content="#f7f4ee" />
</svelte:head>

<article class="story-shell">
	<section class="hero">
		<p class="eyebrow">EDITORIAL DATA STORYTELLING SKILL</p>
		<h1>From raw data to a defensible visual story.</h1>
		<p class="dek">
			This repository is a Pudding-inspired workflow for agents: audit the data, find the claim,
			design the narrative, choose the right visual form, implement it, then validate the result.
		</p>
		<p class="hero-action"><a href="/generated">View the generated baseline →</a></p>
		<div class="hero-grid" aria-label="Skill workflow">
			{#each ["Audit", "Insight", "Narrative", "Visual", "Build", "QA"] as item, i}
				<div class="phase"><span>{String(i + 1).padStart(2, "0")}</span>{item}</div>
			{/each}
		</div>
	</section>

	<section class="principle">
		<div class="principle-copy">
			<p class="kicker">The important change</p>
			<h2>The starter is no longer the skill.</h2>
			<p>
				Svelte is the implementation layer. The reusable value lives in the editorial decisions above it:
				what the evidence supports, how the argument unfolds, and whether scroll is even the right form.
			</p>
		</div>
		<blockquote>“Choose the narrative operation before the chart type.”</blockquote>
	</section>

	<section class="scrolly" aria-label="Synthetic scrollytelling demo">
		<div class="graphic-wrap">
			<div class="graphic">
				<div class="graphic-head">
					<p class="kicker">Synthetic demo · not real-world statistics</p>
					<h2>{states[active].title}</h2>
					<p aria-live="polite">{states[active].note}</p>
				</div>

				<svg viewBox="0 0 640 360" role="img" aria-labelledby="chart-title chart-desc">
					<title id="chart-title">Illustrative pressure index by fictional city</title>
					<desc id="chart-desc">Harbor and Summit are emphasized as the active story reveals a larger synthetic index.</desc>
					<line x1="55" x2="600" y1="286" y2="286" class="baseline" />
					{#each states[active].values as value, i}
						<g class:emphasis={active > 0 && i < 2}>
							<rect x={75 + i * 130} y={286 - value * 3} width="72" height={value * 3} rx="3" />
							<text x={111 + i * 130} y={275 - value * 3} text-anchor="middle" class="value">{value}</text>
							<text x={111 + i * 130} y="318" text-anchor="middle" class="label">{labels[i]}</text>
						</g>
					{/each}
				</svg>
				<p class="chart-note">
					The animation is deliberately simple: one visual state changes at a time, and the conclusion is also stated in text.
				</p>
			</div>
		</div>

		<div class="steps">
			<section class="step" data-story-step="0">
				<p class="step-num">01 · ESTABLISH</p>
				<h3>Give the reader a baseline.</h3>
				<p>Before revealing a difference, show what “same” or “normal” looks like.</p>
			</section>
			<section class="step" data-story-step="1">
				<p class="step-num">02 · REVEAL</p>
				<h3>Change one thing at a time.</h3>
				<p>Preserve the visual frame so the reader can attribute the change to the data rather than the layout.</p>
			</section>
			<section class="step" data-story-step="2">
				<p class="step-num">03 · COMPARE</p>
				<h3>Use emphasis to direct attention.</h3>
				<p>Context remains visible, but the marks that matter to the argument receive the strongest treatment.</p>
			</section>
			<section class="step" data-story-step="3">
				<p class="step-num">04 · CAVEAT</p>
				<h3>Make the boundary of the evidence visible.</h3>
				<p>Strong editorial graphics explain what the data supports and what it cannot establish.</p>
			</section>
		</div>
	</section>

	<section class="cards">
		<div class="section-head">
			<p class="kicker">What the skill decides</p>
			<h2>Scrollytelling is one option, not the default.</h2>
		</div>
		<div class="card-grid">
			<article>
				<span>STATIC</span>
				<h3>Annotated chart</h3>
				<p>Best when one strong pattern carries the story.</p>
			</article>
			<article>
				<span>COMPARE</span>
				<h3>Small multiples</h3>
				<p>Best when readers need aligned repeated comparisons.</p>
			</article>
			<article>
				<span>SEQUENCE</span>
				<h3>Scrollytelling</h3>
				<p>Best when the same visual must transform across narrative beats.</p>
			</article>
			<article>
				<span>EXPLORE</span>
				<h3>Interactive</h3>
				<p>Best when reader-selected lookup or comparison is the purpose.</p>
			</article>
		</div>
	</section>

	<section class="final">
		<p class="kicker">Definition of done</p>
		<h2>A working page is not enough.</h2>
		<p>
			The story must survive data checks, mobile layout, reduced motion, accessibility review, source verification,
			and a final editorial pass. See <code>SKILL.md</code> and <code>references/quality-rubric.md</code>.
		</p>
	</section>
</article>

<Footer storyTitle="Pudding Scrolly" />

<style>
	:global(body) {
		background: #f7f4ee;
		color: #171717;
	}

	.story-shell {
		--accent: #b7452a;
		--ink-soft: #615f59;
		--line: rgba(23, 23, 23, 0.16);
	}

	.hero,
	.principle,
	.cards,
	.final {
		width: min(1120px, calc(100% - 40px));
		margin: 0 auto;
	}

	.hero {
		padding: 11vh 0 13vh;
	}

	.eyebrow,
	.kicker,
	.step-num,
	.card-grid span {
		font-family: var(--font-mono);
		font-size: 0.72rem;
		font-weight: 700;
		letter-spacing: 0.09em;
		text-transform: uppercase;
	}

	.eyebrow,
	.kicker,
	.step-num {
		color: var(--accent);
	}

	h1 {
		max-width: 940px;
		margin: 0.2em 0 0.45em;
		font-family: var(--font-serif);
		font-size: clamp(3rem, 8vw, 7.5rem);
		font-weight: 600;
		letter-spacing: -0.055em;
		line-height: 0.92;
	}

	.dek {
		max-width: 720px;
		font-size: clamp(1.12rem, 2vw, 1.45rem);
		line-height: 1.5;
		color: var(--ink-soft);
	}

	.hero-grid {
		display: grid;
		grid-template-columns: repeat(6, minmax(0, 1fr));
		margin-top: 4rem;
		border-top: 1px solid var(--line);
		border-bottom: 1px solid var(--line);
	}

	.phase {
		padding: 1rem 0.7rem 1.1rem 0;
		font-family: var(--font-sans);
		font-size: 0.88rem;
		font-weight: 700;
	}

	.phase span {
		display: block;
		margin-bottom: 0.35rem;
		font-family: var(--font-mono);
		font-size: 0.66rem;
		color: var(--ink-soft);
	}

	.principle {
		display: grid;
		grid-template-columns: 1.2fr 0.8fr;
		gap: 6vw;
		align-items: end;
		padding: 12vh 0;
		border-top: 1px solid var(--line);
	}

	.principle h2,
	.cards h2,
	.final h2 {
		margin: 0.2em 0 0.5em;
		font-family: var(--font-serif);
		font-size: clamp(2.2rem, 4.4vw, 4.6rem);
		font-weight: 600;
		letter-spacing: -0.04em;
		line-height: 1;
	}

	.principle p,
	.final p {
		max-width: 680px;
		font-size: 1.08rem;
		line-height: 1.65;
		color: var(--ink-soft);
	}

	blockquote {
		margin: 0;
		padding: 0 0 0 1.4rem;
		border-left: 3px solid var(--accent);
		font-family: var(--font-serif);
		font-size: clamp(1.5rem, 2.5vw, 2.35rem);
		font-style: italic;
		line-height: 1.22;
	}

	.scrolly {
		display: grid;
		grid-template-columns: minmax(0, 1.25fr) minmax(280px, 0.75fr);
		gap: 5vw;
		width: min(1260px, calc(100% - 40px));
		margin: 0 auto;
		padding: 10vh 0 14vh;
	}

	.graphic-wrap {
		min-height: 100%;
	}

	.graphic {
		position: sticky;
		top: 9vh;
		padding: clamp(1rem, 3vw, 2.4rem);
		background: #fffefa;
		border: 1px solid var(--line);
		box-shadow: 0 24px 70px rgba(33, 27, 18, 0.08);
	}

	.graphic-head h2 {
		margin: 0.15em 0 0.25em;
		font-family: var(--font-serif);
		font-size: clamp(2rem, 3.5vw, 3.7rem);
		letter-spacing: -0.035em;
		line-height: 1;
	}

	.graphic-head > p:last-child,
	.chart-note {
		max-width: 620px;
		font-family: var(--font-sans);
		font-size: 0.9rem;
		line-height: 1.5;
		color: var(--ink-soft);
	}

	svg {
		margin: 2rem 0 0.5rem;
		overflow: visible;
	}

	.baseline {
		stroke: #b7b2a8;
		stroke-width: 1;
	}

	rect {
		fill: #c8c3b9;
		transition: height 520ms ease, y 520ms ease, fill 300ms ease;
	}

	g.emphasis rect {
		fill: var(--accent);
	}

	.value,
	.label {
		font-family: var(--font-sans);
		fill: #171717;
	}

	.value {
		font-size: 15px;
		font-weight: 700;
		transition: y 520ms ease;
	}

	.label {
		font-size: 14px;
	}

	.steps {
		padding: 18vh 0 24vh;
	}

	.step {
		min-height: 64vh;
		padding: 1.4rem 0 2rem;
		border-top: 1px solid var(--line);
	}

	.step h3 {
		margin: 0.35em 0;
		font-family: var(--font-serif);
		font-size: clamp(1.8rem, 3vw, 3rem);
		line-height: 1.05;
	}

	.step p:last-child {
		font-size: 1rem;
		line-height: 1.65;
		color: var(--ink-soft);
	}

	.cards {
		padding: 12vh 0;
		border-top: 1px solid var(--line);
	}

	.section-head {
		max-width: 820px;
	}

	.card-grid {
		display: grid;
		grid-template-columns: repeat(4, minmax(0, 1fr));
		gap: 1px;
		margin-top: 4rem;
		background: var(--line);
		border: 1px solid var(--line);
	}

	.card-grid article {
		min-height: 260px;
		padding: 1.5rem;
		background: #f7f4ee;
	}

	.card-grid span {
		color: var(--accent);
	}

	.card-grid h3 {
		margin: 1.3rem 0 0.6rem;
		font-family: var(--font-serif);
		font-size: 1.7rem;
		line-height: 1.05;
	}

	.card-grid p {
		line-height: 1.55;
		color: var(--ink-soft);
	}

	.final {
		padding: 12vh 0 16vh;
		border-top: 1px solid var(--line);
	}

	code {
		padding: 0.1em 0.3em;
		font-family: var(--font-mono);
		font-size: 0.88em;
		background: rgba(23, 23, 23, 0.06);
	}

	@media (max-width: 820px) {
		.hero-grid {
			grid-template-columns: repeat(3, 1fr);
		}

		.principle,
		.scrolly {
			grid-template-columns: 1fr;
		}

		.principle {
			gap: 3rem;
		}

		.graphic-wrap {
			position: sticky;
			top: 0;
			z-index: 2;
			margin: 0 -20px;
			padding: 0 20px;
			background: #f7f4ee;
		}

		.graphic {
			top: 0;
			padding: 1rem;
			box-shadow: 0 12px 36px rgba(33, 27, 18, 0.08);
		}

		.graphic-head h2 {
			font-size: 1.75rem;
		}

		.graphic-head > p:last-child,
		.chart-note {
			font-size: 0.8rem;
		}

		svg {
			margin-top: 0.75rem;
		}

		.steps {
			padding-top: 12vh;
		}

		.step {
			min-height: 72vh;
			padding: 1.4rem 0;
		}

		.card-grid {
			grid-template-columns: repeat(2, 1fr);
		}
	}

	@media (max-width: 520px) {
		.hero,
		.principle,
		.cards,
		.final,
		.scrolly {
			width: min(100% - 28px, 1120px);
		}

		.hero-grid {
			grid-template-columns: repeat(2, 1fr);
		}

		.card-grid {
			grid-template-columns: 1fr;
		}

		.card-grid article {
			min-height: 0;
		}
	}

	@media (prefers-reduced-motion: reduce) {
		rect,
		.value {
			transition: none;
		}
	}

	.hero-action { margin-top: 1.5rem; font-family: var(--font-sans); font-weight: 700; }
	.hero-action a { display: inline-block; padding: .75rem 1rem; border: 1px solid currentColor; border-radius: 999px; text-decoration: none; color: inherit; }
	.hero-action a:hover { background: #171717; color: #f7f4ee; }
</style>
