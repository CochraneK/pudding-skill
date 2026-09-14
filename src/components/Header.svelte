<script>
	let { title = "pudding-skill" } = $props();
</script>

<header>
	<div class="title">
		<a href="/" aria-label="Home">{title}</a>
	</div>
</header>

<style>
	.title {
		max-width: var(--width-column, 680px);
		margin: 0 auto;
		padding: 32px 16px;
		font-family: var(--font-sans);
		font-size: var(--20px, 20px);
		font-weight: 700;
	}

	.title a {
		border: none;
		display: block;
		color: var(--color-fg);
		text-decoration: none;
	}

	.title a:hover {
		background-color: transparent;
		opacity: 0.7;
	}
</style>
