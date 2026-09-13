<script>
	let { storyTitle = "Pudding Scrolly" } = $props();
</script>

<footer>
	<div class="c">
		<p>
			Pudding-inspired editorial data storytelling. Starter code derived from
			<a href="https://github.com/the-pudding/svelte-starter">the-pudding/svelte-starter</a> (MIT).
			Not affiliated with The Pudding.
		</p>
		<p class="copyright">&copy; {new Date().getFullYear()} {storyTitle}</p>
	</div>
</footer>

<style>
	footer {
		margin-top: 80px;
		padding: 42px 20px;
		border-top: 1px solid var(--color-border);
		font-family: var(--font-sans);
		font-size: 0.78rem;
		line-height: 1.55;
		color: var(--color-fg-light);
	}

	.c {
		display: flex;
		justify-content: space-between;
		gap: 2rem;
		max-width: 1120px;
		margin: 0 auto;
	}

	p {
		margin: 0;
	}

	a {
		color: inherit;
		text-underline-offset: 0.16em;
	}

	.copyright {
		white-space: nowrap;
	}

	@media (max-width: 700px) {
		.c {
			flex-direction: column;
		}
	}
</style>
