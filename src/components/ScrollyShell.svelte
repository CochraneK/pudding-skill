<script>
	import { onMount } from 'svelte';

	let {
		steps = [],
		graphic,
		step,
		className = '',
		rootMargin = '-42% 0px -42% 0px',
		onactive = () => {}
	} = $props();

	let activeIndex = $state(0);
	let stepElements = $state([]);

	function register(node, index) {
		stepElements[index] = node;
		return {
			destroy() {
				if (stepElements[index] === node) stepElements[index] = null;
			}
		};
	}

	function activate(index) {
		if (index < 0 || index >= steps.length || index === activeIndex) return;
		activeIndex = index;
		onactive?.(index, steps[index]);
	}

	onMount(() => {
		if (!steps.length) return;
		onactive?.(0, steps[0]);

		const observer = new IntersectionObserver(
			(entries) => {
				const visible = entries
					.filter((entry) => entry.isIntersecting)
					.sort((a, b) => b.intersectionRatio - a.intersectionRatio);
				if (!visible.length) return;
				const next = Number(visible[0].target.dataset.scrollyIndex);
				if (Number.isInteger(next)) activate(next);
			},
			{ rootMargin, threshold: [0, 0.01, 0.25, 0.5, 0.75] }
		);

		stepElements.filter(Boolean).forEach((node) => observer.observe(node));
		return () => observer.disconnect();
	});
</script>

<div class={`scrolly-shell ${className}`.trim()} data-scrolly-shell>
	<div class="scrolly-shell__graphic" aria-live="off">
		<div class="scrolly-shell__stage">
			{#if graphic}
				{@render graphic(steps[activeIndex], activeIndex)}
			{/if}
		</div>
	</div>

	<div class="scrolly-shell__steps">
		{#each steps as item, index (item.id ?? index)}
			<section
				class:active={index === activeIndex}
				class="scrolly-shell__step"
				data-scrolly-index={index}
				data-step-id={item.id ?? `step-${index + 1}`}
				aria-current={index === activeIndex ? 'step' : undefined}
				use:register={index}
			>
				<div class="scrolly-shell__step-card">
					{#if step}
						{@render step(item, index, index === activeIndex)}
					{:else}
						{#if item.kicker}<p class="scrolly-shell__kicker">{item.kicker}</p>{/if}
						{#if item.title}<h2>{item.title}</h2>{/if}
						{#if item.text}<p>{item.text}</p>{/if}
					{/if}
				</div>
			</section>
		{/each}
	</div>
</div>

<style>
	.scrolly-shell {
		width: min(100% - 2rem, 78rem);
		margin-inline: auto;
		display: grid;
		grid-template-columns: minmax(0, 1.42fr) minmax(18rem, 0.8fr);
		gap: clamp(2rem, 6vw, 6rem);
		align-items: start;
	}

	.scrolly-shell__graphic {
		position: sticky;
		top: 0;
		height: 100svh;
		display: grid;
		align-items: center;
		min-width: 0;
	}

	.scrolly-shell__stage {
		width: 100%;
		min-height: min(72svh, 44rem);
		display: grid;
		align-content: center;
		min-width: 0;
	}

	.scrolly-shell__steps {
		padding-block: 12svh;
		min-width: 0;
	}

	.scrolly-shell__step {
		min-height: 88svh;
		display: flex;
		align-items: center;
		opacity: 0.38;
		transition: opacity 220ms ease;
	}

	.scrolly-shell__step.active {
		opacity: 1;
	}

	.scrolly-shell__step-card {
		width: 100%;
		padding-block: 1.25rem;
	}

	.scrolly-shell__kicker {
		margin: 0 0 0.6rem;
		font: 700 0.75rem/1.2 var(--font-sans, system-ui, sans-serif);
		letter-spacing: 0.12em;
		text-transform: uppercase;
		opacity: 0.68;
	}

	.scrolly-shell__step-card :global(h2) {
		margin: 0 0 0.65em;
		font-size: clamp(1.8rem, 3vw, 2.7rem);
		line-height: 1.12;
	}

	.scrolly-shell__step-card :global(p) {
		font-size: 1.05rem;
		line-height: 1.75;
	}

	@media (max-width: 56rem) {
		.scrolly-shell {
			display: block;
			width: min(100% - 1rem, 46rem);
		}

		.scrolly-shell__graphic {
			height: 50svh;
			top: 0;
			z-index: 2;
		}

		.scrolly-shell__stage {
			min-height: 46svh;
		}

		.scrolly-shell__steps {
			padding-block: 0 8svh;
		}

		.scrolly-shell__step {
			min-height: 72svh;
			align-items: flex-end;
			position: relative;
			z-index: 3;
			padding-bottom: 8svh;
		}

		.scrolly-shell__step-card {
			padding: 1.1rem;
			border-radius: 1rem;
			background: color-mix(in srgb, var(--color-bg, #fff) 94%, transparent);
			backdrop-filter: blur(10px);
			box-shadow: 0 0.75rem 2.5rem rgb(0 0 0 / 0.08);
		}
	}

	@media (prefers-reduced-motion: reduce) {
		.scrolly-shell__step {
			transition: none;
		}
	}
</style>
