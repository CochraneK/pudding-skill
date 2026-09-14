<script>
	import ScrollyShell from '$components/ScrollyShell.svelte';

	const steps = [
		{
			id: 'establish',
			kicker: '01 · establish',
			title: 'One frame, one baseline',
			text: 'The graphic remains spatially stable while the narrative advances.',
			value: 24,
			status: 'OBSERVED'
		},
		{
			id: 'compare',
			kicker: '02 · compare',
			title: 'Change the evidence state, not the scroll physics',
			text: 'Each step is complete and can be entered directly or while scrolling backward.',
			value: 62,
			status: 'DERIVED'
		},
		{
			id: 'qualify',
			kicker: '03 · qualify',
			title: 'Keep uncertainty visible in the dramatic state',
			text: 'Evidence status remains attached to the number instead of being buried in a footer.',
			value: 81,
			status: 'SCENARIO'
		}
	];
</script>

<svelte:head>
	<title>Scrolly shell specimen · Pudding Skill</title>
	<meta
		name="description"
		content="A neutral specimen route for the reusable guided sticky-scroll shell."
	/>
</svelte:head>

<header class="intro">
	<p class="eyebrow">Interaction specimen</p>
	<h1>Reusable sticky-scroll shell</h1>
	<p>
		This route contains no story claim. It exists to compile and visually inspect the interaction grammar
		learned from a supplied single-file HTML scrolly.
	</p>
</header>

{#snippet graphic(item, index)}
	<div class="graphic-card" data-active-state={item?.id}>
		<p class="status">{item?.status}</p>
		<div class="value">{item?.value ?? '—'}</div>
		<div class="rail" aria-hidden="true">
			<div class="fill" style={`width:${item?.value ?? 0}%`}></div>
		</div>
		<p class="state-label">State {index + 1} · {item?.id}</p>
	</div>
{/snippet}

{#snippet step(item)}
	<p class="step-kicker">{item.kicker}</p>
	<h2>{item.title}</h2>
	<p>{item.text}</p>
	<p class="evidence-status">Evidence status: <strong>{item.status}</strong></p>
{/snippet}

<ScrollyShell {steps} {graphic} {step} />

<section class="after">
	<h2>What this specimen proves</h2>
	<p>
		The component owns natural scroll observation and responsive layout. Story code owns evidence,
		visual state, prose, and claim provenance. If a static prototype wins the tournament, do not use this
		component.
	</p>
</section>

<style>
	.intro,
	.after {
		width: min(100% - 2rem, 48rem);
		margin-inline: auto;
		padding-block: 12svh;
	}

	.eyebrow,
	.step-kicker,
	.status,
	.evidence-status,
	.state-label {
		font-family: var(--font-sans);
		font-size: 0.75rem;
		letter-spacing: 0.1em;
		text-transform: uppercase;
	}

	.intro h1 {
		font-size: clamp(2.8rem, 8vw, 6.5rem);
		line-height: 0.95;
		letter-spacing: -0.04em;
		margin: 0.2em 0;
	}

	.intro > p:last-child,
	.after p {
		font-size: 1.15rem;
		line-height: 1.75;
	}

	.graphic-card {
		padding: clamp(1.5rem, 4vw, 3rem);
		border: 1px solid var(--color-border);
		border-radius: 1.5rem;
		background: var(--color-bg);
		box-shadow: 0 2rem 5rem rgb(0 0 0 / 0.08);
	}

	.status,
	.state-label,
	.evidence-status {
		color: var(--color-fg-light);
	}

	.value {
		font-family: var(--font-sans);
		font-size: clamp(5rem, 13vw, 10rem);
		font-weight: 800;
		line-height: 0.9;
		font-variant-numeric: tabular-nums;
	}

	.rail {
		height: 1rem;
		border-radius: 999px;
		background: color-mix(in srgb, var(--color-fg) 10%, transparent);
		overflow: hidden;
		margin-block: 1.5rem 1rem;
	}

	.fill {
		height: 100%;
		background: currentColor;
		transition: width 240ms ease;
	}

	.step-kicker {
		color: var(--color-fg-light);
	}

	.evidence-status strong {
		color: var(--color-fg);
	}

	.after {
		padding-bottom: 18svh;
	}

	@media (prefers-reduced-motion: reduce) {
		.fill {
			transition: none;
		}
	}
</style>
