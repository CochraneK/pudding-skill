<script>
	let { storyTitle = "Scrollytelling Story" } = $props();
</script>

<footer>
	<div class="c">
		<div class="bottom">
			<section class="links">
				<div class="inner">
					<p>Built with <a href="https://pudding.cool">the-pudding/svelte-starter</a> + <a href="https://layercake.graphics/">LayerCake</a></p>
				</div>
			</section>
			<p class="copyright">&copy; {new Date().getFullYear()} {storyTitle}</p>
		</div>
	</div>
</footer>

<style>
	footer {
		margin-top: 100px;
		padding: 48px 16px;
		border-top: 1px solid var(--color-fg);
		opacity: 0.6;
		font-family: var(--font-sans);
		font-size: var(--14px, 14px);
	}

	.c {
		max-width: calc(var(--width-column-wide, 1280px) - var(--margin, 16px) * 2);
		margin: 0 auto;
	}

	.bottom {
		display: flex;
		flex-direction: column;
		align-items: center;
		text-align: center;
		gap: 8px;
	}

	.links {
		width: 100%;
	}

	.links .inner {
		display: flex;
		justify-content: center;
		gap: 16px;
	}

	a {
		font-weight: 700;
		color: var(--color-fg);
		text-decoration: 2px underline var(--color-fg);
	}

	a:hover {
		color: var(--color-link-hover);
		text-decoration: 2px underline var(--color-link-hover);
	}

	.copyright {
		color: var(--color-fg);
		margin: 0;
	}
</style>
