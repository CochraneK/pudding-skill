<script>
	import { base } from '$app/paths';
	import Meta from '$components/Meta.svelte';
	import reportIndex from '$data/report-index.json';

	const hrefFor = (route) => `${base}${route}`;
	const reports = reportIndex.reports;
</script>

<Meta
	title="Pudding Reports — 数据故事"
	description="A single public index for evidence-audited data stories built with pudding-skill."
	url="https://cochranek.github.io/pudding-skill/"
/>

<svelte:head>
	<meta name="theme-color" content="#f4efe6" />
</svelte:head>

<article class="report-hub">
	<section class="hero">
		<p class="eyebrow">PUDDING-SKILL · PUBLIC REPORTS</p>
		<h1>Data stories,<br /><em>in one place.</em></h1>
		<p class="dek">{reportIndex.site_dek}</p>
		<div class="hero-meta" aria-label="Report library summary">
			<span><strong>{reports.length}</strong> published report</span>
			<span>GitHub Pages · free public hosting</span>
			<span>Evidence + method + QA kept visible</span>
		</div>
	</section>

	<section class="reports" aria-labelledby="reports-title">
		<div class="section-head">
			<p class="eyebrow">REPORT LIBRARY</p>
			<h2 id="reports-title">当前报告</h2>
			<p>以后新增的报告只需要注册到同一个 report index，这里会继续作为统一入口。</p>
		</div>

		{#each reports as report, i}
			<article class="report-card">
				<div class="report-number">{String(i + 1).padStart(2, '0')}</div>
				<div class="report-copy">
					<div class="report-topline">
						<span>{report.eyebrow}</span>
						<span class="status">{report.status} · {report.published}</span>
					</div>
					<h3>{report.title}</h3>
					<p class="subtitle">{report.subtitle}</p>
					<p class="report-dek">{report.dek}</p>

					<div class="stats" aria-label={`${report.title} key figures`}>
						{#each report.stats as stat}
							<div>
								<strong>{stat.value}</strong>
								<span>{stat.label}</span>
							</div>
						{/each}
					</div>

					<div class="actions">
						<a class="primary" href={hrefFor(report.primary_route)}>阅读完整报告 →</a>
						{#each report.secondary_routes as route}
							<a href={hrefFor(route.route)}>{route.label} ↗</a>
						{/each}
					</div>

					<div class="tags" aria-label="Report sources and themes">
						{#each report.tags as tag}<span>{tag}</span>{/each}
					</div>
				</div>
			</article>
		{/each}
	</section>

	<section class="architecture" aria-labelledby="architecture-title">
		<div>
			<p class="eyebrow">BUILT FOR THE NEXT REPORT</p>
			<h2 id="architecture-title">一个网址，持续增加报告。</h2>
		</div>
		<div class="architecture-grid">
			<article>
				<span>01</span>
				<h3>统一首页</h3>
				<p>所有正式报告从这里进入，不再把读者送进开发用的 demo、lab 或 benchmark。</p>
			</article>
			<article>
				<span>02</span>
				<h3>报告注册表</h3>
				<p>新增报告时增加一条元数据即可进入公共目录，标题、摘要、状态和关键数字都集中维护。</p>
			</article>
			<article>
				<span>03</span>
				<h3>独立深读页面</h3>
				<p>长报告仍保留自己的叙事空间；地图、atlas 或附录可作为报告模块，而首页负责统一发现。</p>
			</article>
		</div>
	</section>

	<footer class="hub-footer">
		<p>Built with <strong>pudding-skill</strong> · editorial data storytelling with auditable evidence.</p>
		<nav aria-label="Developer routes">
			<a href={hrefFor('/demo')}>Demo</a>
			<a href={hrefFor('/lab')}>Lab</a>
			<a href={hrefFor('/benchmark')}>Benchmark</a>
		</nav>
	</footer>
</article>

<style>
	:global(body) {
		background: #f4efe6;
		color: #171715;
	}

	.report-hub {
		--paper: #f4efe6;
		--panel: #fffaf2;
		--ink: #171715;
		--muted: #68645d;
		--accent: #a33f32;
		--line: #d6cec1;
		min-height: 100vh;
	}

	.hero,
	.reports,
	.architecture,
	.hub-footer {
		width: min(1180px, calc(100% - 40px));
		margin: 0 auto;
	}

	.hero {
		padding: clamp(5rem, 11vw, 10rem) 0 clamp(5rem, 9vw, 8rem);
	}

	.eyebrow,
	.report-topline,
	.tags,
	.architecture-grid > article > span {
		font-family: var(--font-mono);
		font-size: 0.72rem;
		font-weight: 750;
		letter-spacing: 0.1em;
		text-transform: uppercase;
	}

	.eyebrow,
	.report-topline > span:first-child {
		color: var(--accent);
	}

	h1,
	h2,
	h3 {
		font-family: var(--font-serif);
	}

	h1 {
		max-width: 1000px;
		margin: 0.18em 0 0.3em;
		font-size: clamp(4rem, 11vw, 9.4rem);
		font-weight: 600;
		line-height: 0.84;
		letter-spacing: -0.065em;
	}

	h1 em {
		color: var(--accent);
		font-weight: 400;
	}

	.dek {
		max-width: 720px;
		font-size: clamp(1.12rem, 2vw, 1.45rem);
		line-height: 1.58;
		color: var(--muted);
	}

	.hero-meta {
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		margin-top: 4rem;
		border-top: 1px solid var(--line);
		border-bottom: 1px solid var(--line);
	}

	.hero-meta span {
		padding: 1rem 1rem 1rem 0;
		font-family: var(--font-sans);
		font-size: 0.86rem;
		line-height: 1.45;
		color: var(--muted);
	}

	.hero-meta strong {
		color: var(--ink);
	}

	.reports {
		padding: 7rem 0;
		border-top: 1px solid var(--line);
	}

	.section-head {
		display: grid;
		grid-template-columns: 1fr 1fr;
		column-gap: 3rem;
		align-items: end;
		margin-bottom: 3rem;
	}

	.section-head .eyebrow {
		grid-column: 1 / -1;
	}

	.section-head h2,
	.architecture h2 {
		margin: 0.2em 0 0;
		font-size: clamp(2.6rem, 6vw, 5.6rem);
		line-height: 0.94;
		letter-spacing: -0.045em;
	}

	.section-head > p:last-child {
		max-width: 52ch;
		margin: 0;
		color: var(--muted);
		line-height: 1.6;
	}

	.report-card {
		display: grid;
		grid-template-columns: minmax(80px, 0.15fr) minmax(0, 1fr);
		gap: 1.5rem;
		padding: clamp(1.5rem, 4vw, 3rem) 0 0;
		border-top: 1px solid var(--line);
	}

	.report-number {
		font-family: var(--font-mono);
		font-size: clamp(2.5rem, 6vw, 5rem);
		font-weight: 700;
		letter-spacing: -0.06em;
		color: #b8aea0;
	}

	.report-copy {
		padding: 0 0 4rem;
	}

	.report-topline {
		display: flex;
		justify-content: space-between;
		gap: 1rem;
	}

	.status {
		color: var(--muted);
	}

	.report-card h3 {
		margin: 1rem 0 0;
		font-size: clamp(3rem, 7vw, 6.8rem);
		line-height: 0.92;
		letter-spacing: -0.05em;
	}

	.subtitle {
		margin: 0.5rem 0 1.5rem;
		font: 500 clamp(1.35rem, 2.6vw, 2.2rem)/1.15 var(--font-serif);
		font-style: italic;
		color: var(--accent);
	}

	.report-dek {
		max-width: 760px;
		font-size: 1.08rem;
		line-height: 1.65;
		color: var(--muted);
	}

	.stats {
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		margin: 3rem 0;
		border: 1px solid var(--line);
		background: var(--panel);
	}

	.stats > div {
		padding: 1.5rem;
		border-right: 1px solid var(--line);
	}

	.stats > div:last-child {
		border-right: 0;
	}

	.stats strong,
	.stats span {
		display: block;
	}

	.stats strong {
		font: 800 clamp(2.4rem, 5vw, 4.8rem)/0.95 var(--font-sans);
		letter-spacing: -0.055em;
		color: var(--accent);
	}

	.stats span {
		max-width: 26ch;
		margin-top: 0.8rem;
		font-family: var(--font-sans);
		font-size: 0.82rem;
		line-height: 1.45;
		color: var(--muted);
	}

	.actions {
		display: flex;
		flex-wrap: wrap;
		gap: 0.7rem;
	}

	.actions a {
		display: inline-flex;
		align-items: center;
		min-height: 44px;
		padding: 0.7rem 1rem;
		border: 1px solid var(--ink);
		font-family: var(--font-sans);
		font-size: 0.9rem;
		font-weight: 750;
		color: var(--ink);
		text-decoration: none;
	}

	.actions a.primary {
		background: var(--ink);
		color: var(--paper);
	}

	.actions a:hover {
		transform: translateY(-1px);
	}

	.tags {
		display: flex;
		flex-wrap: wrap;
		gap: 0.45rem;
		margin-top: 1.5rem;
		color: var(--muted);
	}

	.tags span::after {
		content: ' ·';
	}

	.tags span:last-child::after {
		content: '';
	}

	.architecture {
		display: grid;
		grid-template-columns: 0.9fr 1.1fr;
		gap: 5vw;
		padding: 8rem 0;
		border-top: 1px solid var(--line);
	}

	.architecture-grid {
		display: grid;
		gap: 0;
		border-top: 1px solid var(--line);
	}

	.architecture-grid article {
		padding: 1.5rem 0;
		border-bottom: 1px solid var(--line);
	}

	.architecture-grid h3 {
		margin: 0.3rem 0 0.5rem;
		font-size: 1.8rem;
	}

	.architecture-grid p {
		max-width: 56ch;
		margin: 0;
		line-height: 1.6;
		color: var(--muted);
	}

	.hub-footer {
		display: flex;
		justify-content: space-between;
		gap: 2rem;
		padding: 2rem 0 4rem;
		border-top: 1px solid var(--line);
		font-family: var(--font-sans);
		font-size: 0.82rem;
		color: var(--muted);
	}

	.hub-footer nav {
		display: flex;
		gap: 1rem;
	}

	.hub-footer a {
		color: inherit;
	}

	@media (max-width: 760px) {
		.hero-meta,
		.section-head,
		.architecture,
		.stats {
			grid-template-columns: 1fr;
		}

		.hero-meta span + span,
		.stats > div + div {
			border-top: 1px solid var(--line);
		}

		.stats > div {
			border-right: 0;
		}

		.section-head > p:last-child {
			margin-top: 1rem;
		}

		.report-card {
			grid-template-columns: 1fr;
		}

		.report-number {
			font-size: 2rem;
		}

		.report-topline,
		.hub-footer {
			flex-direction: column;
		}

		.architecture-grid {
			margin-top: 2rem;
		}
	}
</style>
