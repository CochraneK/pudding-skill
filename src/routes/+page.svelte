<script>
	import { base } from '$app/paths';
	import Meta from '$components/Meta.svelte';
	import LanguageToggle from '$components/LanguageToggle.svelte';
	import reportIndex from '$data/report-index.json';
	import { language } from '$lib/language.js';

	const hrefFor = (route) => `${base}${route}`;
	const reports = reportIndex.reports;
	const localize = (value) => typeof value === 'object' && value !== null && !Array.isArray(value) ? value[$language] : value;

	const copy = {
		zh: {
			eyebrow: 'PUDDING-SKILL · 公共报告库',
			titleLead: 'Data stories,',
			titleEm: 'in one place.',
			published: '份已发布报告',
			hosting: 'GitHub Pages · 免费公开托管',
			qa: '证据 + 方法 + 交互 + QA 保持可见',
			library: '报告库',
			libraryTitle: '当前报告',
			libraryDek: '正式报告从这里进入；开发用 demo、lab 和 benchmark 保持在后台，不打断阅读。',
			read: '阅读完整报告 →',
			architecture: '为下一份报告准备',
			architectureTitle: '一个网址，持续增加报告。',
			cards: [
				['统一入口', '首页只负责发现与进入。每个正式报告拥有自己的完整叙事空间。'],
				['双语注册表', '标题、摘要、关键数字和路由集中维护，中英文从同一份元数据生成。'],
				['静态 / 引导 / 探索', '形式由编辑任务决定：能静态讲清就不强加交互；只有交互真正增加理解时，才加入引导或探索。']
			],
			footer: 'Built with pudding-skill · 可审计证据驱动的数据叙事。'
		},
		en: {
			eyebrow: 'PUDDING-SKILL · PUBLIC REPORTS',
			titleLead: 'Data stories,',
			titleEm: 'in one place.',
			published: 'published report',
			hosting: 'GitHub Pages · free public hosting',
			qa: 'Evidence + method + interaction + QA stay visible',
			library: 'REPORT LIBRARY',
			libraryTitle: 'Current reports',
			libraryDek: 'Published reports start here. Developer surfaces such as demo, lab, and benchmark stay in the background instead of interrupting readers.',
			read: 'Read the full report →',
			architecture: 'BUILT FOR THE NEXT REPORT',
			architectureTitle: 'One URL, a growing report library.',
			cards: [
				['One public entrance', 'The homepage handles discovery. Each published report keeps its own full narrative space.'],
				['Bilingual registry', 'Titles, summaries, key figures, and routes live in one registry and render in Chinese or English.'],
				['Static / guided / explorable', 'Form follows the editorial task: stay static when that is enough, and add guidance or exploration only when interaction earns its complexity.']
			],
			footer: 'Built with pudding-skill · auditable evidence-driven data storytelling.'
		}
	};

	const t = () => copy[$language];
</script>

<Meta
	title="Pudding Reports — 数据故事"
	description={localize(reportIndex.site_dek)}
	url="https://cochranek.github.io/pudding-skill/"
/>

<svelte:head>
	<meta name="theme-color" content="#f4efe6" />
</svelte:head>

<article class="report-hub">
	<section class="hero">
		<div class="utility"><span>{t().eyebrow}</span><LanguageToggle /></div>
		<h1>{t().titleLead}<br /><em>{t().titleEm}</em></h1>
		<p class="dek">{localize(reportIndex.site_dek)}</p>
		<div class="hero-meta" aria-label={$language === 'zh' ? '报告库摘要' : 'Report library summary'}>
			<span><strong>{reports.length}</strong> {t().published}</span>
			<span>{t().hosting}</span>
			<span>{t().qa}</span>
		</div>
	</section>

	<section class="reports" aria-labelledby="reports-title">
		<div class="section-head">
			<p class="eyebrow">{t().library}</p>
			<h2 id="reports-title">{t().libraryTitle}</h2>
			<p>{t().libraryDek}</p>
		</div>

		{#each reports as report, i}
			<article class="report-card">
				<div class="report-number">{String(i + 1).padStart(2, '0')}</div>
				<div class="report-copy">
					<div class="report-topline">
						<span>{localize(report.eyebrow)}</span>
						<span class="status">{localize(report.status)} · {report.published}</span>
					</div>
					<h3>{localize(report.title)}</h3>
					<p class="subtitle">{localize(report.subtitle)}</p>
					<p class="report-dek">{localize(report.dek)}</p>

					<div class="stats" aria-label={`${localize(report.title)} key figures`}>
						{#each report.stats as stat}
							<div><strong>{stat.value}</strong><span>{localize(stat.label)}</span></div>
						{/each}
					</div>

					<div class="actions">
						<a class="primary" href={hrefFor(report.primary_route)}>{t().read}</a>
						{#each report.secondary_routes as route}
							<a href={hrefFor(route.route)}>{localize(route.label)} ↗</a>
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
			<p class="eyebrow">{t().architecture}</p>
			<h2 id="architecture-title">{t().architectureTitle}</h2>
		</div>
		<div class="architecture-grid">
			{#each t().cards as card, i}
				<article>
					<span>0{i + 1}</span>
					<h3>{card[0]}</h3>
					<p>{card[1]}</p>
				</article>
			{/each}
		</div>
	</section>

	<footer class="hub-footer">
		<p>{t().footer}</p>
		<nav aria-label="Developer routes">
			<a href={hrefFor('/demo')}>Demo</a>
			<a href={hrefFor('/lab')}>Lab</a>
			<a href={hrefFor('/benchmark')}>Benchmark</a>
		</nav>
	</footer>
</article>

<style>
	:global(body) { background: #f4efe6; color: #171715; }
	.report-hub { --paper:#f4efe6; --panel:#fffaf2; --ink:#171715; --muted:#68645d; --accent:#a33f32; --line:#d6cec1; min-height:100vh; }
	.hero,.reports,.architecture,.hub-footer { width:min(1180px,calc(100% - 40px)); margin:0 auto; }
	.hero { padding:clamp(3rem,7vw,6rem) 0 clamp(5rem,9vw,8rem); }
	.utility { display:flex; justify-content:space-between; gap:1rem; align-items:center; margin-bottom:clamp(5rem,10vw,9rem); font:750 .72rem/1.2 var(--font-mono); letter-spacing:.1em; color:var(--accent); }
	.eyebrow,.report-topline,.tags,.architecture-grid>article>span { font-family:var(--font-mono); font-size:.72rem; font-weight:750; letter-spacing:.1em; text-transform:uppercase; }
	.eyebrow,.report-topline>span:first-child { color:var(--accent); }
	h1,h2,h3 { font-family:var(--font-serif); }
	h1 { max-width:1000px; margin:.18em 0 .3em; font-size:clamp(4rem,11vw,9.4rem); font-weight:600; line-height:.84; letter-spacing:-.065em; }
	h1 em { color:var(--accent); font-weight:400; }
	.dek { max-width:760px; font-size:clamp(1.12rem,2vw,1.45rem); line-height:1.58; color:var(--muted); }
	.hero-meta { display:grid; grid-template-columns:repeat(3,1fr); margin-top:4rem; border-top:1px solid var(--line); border-bottom:1px solid var(--line); }
	.hero-meta span { padding:1rem 1rem 1rem 0; font:500 .86rem/1.45 var(--font-sans); color:var(--muted); }
	.hero-meta strong { color:var(--ink); }
	.reports { padding:7rem 0; border-top:1px solid var(--line); }
	.section-head { display:grid; grid-template-columns:1fr 1fr; column-gap:3rem; align-items:end; margin-bottom:3rem; }
	.section-head .eyebrow { grid-column:1/-1; }
	.section-head h2,.architecture h2 { margin:.2em 0 0; font-size:clamp(2.6rem,6vw,5.6rem); line-height:.94; letter-spacing:-.045em; }
	.section-head>p:last-child { max-width:52ch; margin:0; color:var(--muted); line-height:1.6; }
	.report-card { display:grid; grid-template-columns:minmax(80px,.15fr) minmax(0,1fr); gap:1.5rem; padding:clamp(1.5rem,4vw,3rem) 0 0; border-top:1px solid var(--line); }
	.report-number { font:700 clamp(2.5rem,6vw,5rem)/1 var(--font-mono); letter-spacing:-.06em; color:#b8aea0; }
	.report-copy { padding:0 0 4rem; }
	.report-topline { display:flex; justify-content:space-between; gap:1rem; }
	.status { color:var(--muted); }
	.report-card h3 { margin:1rem 0 0; font-size:clamp(3rem,7vw,6.8rem); line-height:.92; letter-spacing:-.05em; }
	.subtitle { margin:.5rem 0 1.5rem; font:500 clamp(1.35rem,2.6vw,2.2rem)/1.15 var(--font-serif); font-style:italic; color:var(--accent); }
	.report-dek { max-width:760px; font-size:1.08rem; line-height:1.65; color:var(--muted); }
	.stats { display:grid; grid-template-columns:repeat(3,1fr); margin:3rem 0; border:1px solid var(--line); background:var(--panel); }
	.stats>div { padding:1.5rem; border-right:1px solid var(--line); }
	.stats>div:last-child { border-right:0; }
	.stats strong,.stats span { display:block; }
	.stats strong { font:800 clamp(2.4rem,5vw,4.8rem)/.95 var(--font-sans); letter-spacing:-.055em; color:var(--accent); }
	.stats span { max-width:28ch; margin-top:.8rem; font:500 .82rem/1.45 var(--font-sans); color:var(--muted); }
	.actions { display:flex; flex-wrap:wrap; gap:.7rem; }
	.actions a { display:inline-flex; align-items:center; min-height:44px; padding:.7rem 1rem; border:1px solid var(--ink); font:750 .9rem/1.2 var(--font-sans); color:var(--ink); text-decoration:none; }
	.actions a.primary { background:var(--ink); color:var(--paper); }
	.actions a:hover { transform:translateY(-1px); }
	.tags { display:flex; flex-wrap:wrap; gap:.45rem; margin-top:1.5rem; color:var(--muted); }
	.tags span::after { content:' ·'; } .tags span:last-child::after { content:''; }
	.architecture { display:grid; grid-template-columns:.9fr 1.1fr; gap:5vw; padding:8rem 0; border-top:1px solid var(--line); }
	.architecture-grid { display:grid; border-top:1px solid var(--line); }
	.architecture-grid article { padding:1.5rem 0; border-bottom:1px solid var(--line); }
	.architecture-grid h3 { margin:.3rem 0 .5rem; font-size:1.8rem; }
	.architecture-grid p { max-width:56ch; margin:0; line-height:1.6; color:var(--muted); }
	.hub-footer { display:flex; justify-content:space-between; gap:2rem; padding:2rem 0 4rem; border-top:1px solid var(--line); font:500 .82rem/1.4 var(--font-sans); color:var(--muted); }
	.hub-footer nav { display:flex; gap:.35rem; flex-wrap:wrap; } .hub-footer a { display:inline-flex; align-items:center; min-width:44px; min-height:44px; padding:0 .35rem; color:inherit; }
	@media(max-width:760px){ .hero-meta,.section-head,.architecture,.stats{grid-template-columns:1fr}.hero-meta span+span,.stats>div+div{border-top:1px solid var(--line)}.stats>div{border-right:0}.section-head>p:last-child{margin-top:1rem}.report-card{grid-template-columns:1fr}.report-number{font-size:2rem}.report-topline,.hub-footer{flex-direction:column}.architecture-grid{margin-top:2rem} }
</style>
