<script>
	import { base } from '$app/paths';
	import facts from '$data/global-mental-health-facts.json';
	import LanguageToggle from '$components/LanguageToggle.svelte';
	import GlobalMentalHealthScrolly from '$components/GlobalMentalHealthScrolly.svelte';
	import GlobalMentalHealthExplorer from '$components/GlobalMentalHealthExplorer.svelte';
	import { language } from '$lib/language.js';

	const source = (id) => facts.sources[id];

	const copy = {
		zh: {
			back: '← 返回报告库',
			eyebrow: '全球精神健康 · 研究档案数据故事',
			titleLead: '世界的',
			titleEm: '隐形负担',
			dek: '超过 10 亿人生活在精神障碍之中。更尖锐的全球差距，不只是“哪里患病率高”，而是谁拥有足够的资金、专业人员与社区服务去回应需要。',
			heroLabel: '2021 年全球精神障碍患者',
			heroDetail: 'WHO 报告年龄标化患病率约 13.6%，接近每 7 人就有 1 人。',
			scrollCue: '向下滚动，让同一张图一步一步改变。',
			transitionEyebrow: '从作者引导 → 读者探索',
			transitionTitle: 'Pudding 式交互，不应该止于动画。',
			transitionBody: '前半段由滚动控制视觉状态，让读者按叙事顺序建立尺度感；到了这里，控制权交还给读者。接下来的地图可以自己切换指标、查看国家和年份。引导与探索使用的是同一套经过审计的数据，而不是两个互不相干的“图表页面”。',
			methodEyebrow: '别让交互制造虚假的确定性',
			methodTitle: '这张地图能比较系统能力，但不能给国家贴“心理健康好坏”的标签。',
			methodCards: [
				['患病率 ≠ 诊断率', 'GBD/WHO 的患病率是模型估计，不是已诊断病例登记，也不是国家幸福度评分。'],
				['缺失 ≠ 0', 'WHO 指标覆盖率不同。没有报告的数据保持灰色，不用插值或 0 替代。'],
				['年份必须一起看', '国家级人力和服务指标主要来自较早 Atlas/GHO 轮次。跨国比较前先看报告年份。'],
				['相关 ≠ 因果', '需求高、资源少可能同时出现，但这张图本身不能证明资源不足造成了某个患病率。']
			],
			sourcesEyebrow: '来源与证据链',
			sourcesTitle: '每个关键数字都能追溯回原始来源。',
			sourceNote: '报告中的数字来自 WHO、IHME/GBD 与同行评议研究。完整的 source ledger、numeric evidence 和 data-acquisition plan 保存在仓库的 Research Dossier 中。',
			standalone: '打开独立 Capacity Atlas →',
			status: '研究支持的交互式数据故事 · 数据、口径和缺失保持可见'
		},
		en: {
			back: '← Back to report library',
			eyebrow: 'GLOBAL MENTAL HEALTH · RESEARCH DOSSIER STORY',
			titleLead: "The world's",
			titleEm: 'invisible burden',
			dek: 'More than a billion people live with mental disorders. The sharper global divide is not simply where prevalence is higher, but whether care systems have the money, people and community services to respond.',
			heroLabel: 'people living with a mental disorder in 2021',
			heroDetail: 'WHO reports an age-standardized prevalence of 13.6% — nearly one in seven people worldwide.',
			scrollCue: 'Scroll down. The same graphic will change one argument at a time.',
			transitionEyebrow: 'FROM AUTHOR GUIDANCE → READER EXPLORATION',
			transitionTitle: 'Pudding-style interaction should not stop at animation.',
			transitionBody: 'The first half lets scrolling control visual state so the reader builds context in a deliberate order. Here, control shifts back to the reader. The map below lets you switch indicators and inspect countries and reporting years. Guidance and exploration use the same audited evidence rather than two disconnected chart pages.',
			methodEyebrow: 'DO NOT LET INTERACTION CREATE FALSE CERTAINTY',
			methodTitle: 'This map compares system capacity. It does not rank countries by “mental health.”',
			methodCards: [
				['Prevalence ≠ diagnosis', 'GBD/WHO prevalence is modeled evidence, not a registry of diagnosed cases and not a national wellbeing score.'],
				['Missing ≠ zero', 'WHO indicator coverage differs. Missing observations stay gray; they are never imputed or silently converted to zero.'],
				['Read the year', 'Country workforce and service indicators largely come from earlier Atlas/GHO rounds. Read reporting year before comparing countries.'],
				['Association ≠ causation', 'High need and low capacity can coexist, but this visualization cannot prove that resource scarcity caused a prevalence level.']
			],
			sourcesEyebrow: 'SOURCES + PROVENANCE',
			sourcesTitle: 'Every material number can be traced back to its source.',
			sourceNote: 'The story uses WHO, IHME/GBD, and peer-reviewed evidence. The repository keeps the full source ledger, numeric evidence table, and data-acquisition plan in the Research Dossier.',
			standalone: 'Open the standalone Capacity Atlas →',
			status: 'Research-backed interactive data story · data, definitions, and missingness remain visible'
		}
	};

	const t = () => copy[$language];
</script>

<svelte:head>
	<title>{t().titleLead} {t().titleEm} · pudding-skill</title>
	<meta
		name="description"
		content={t().dek}
	/>
	<meta property="og:title" content={`${t().titleLead} ${t().titleEm}`} />
	<meta property="og:description" content={t().dek} />
	<meta name="theme-color" content="#f5f0e7" />
	<link rel="canonical" href="https://cochranek.github.io/pudding-skill/stories/global-mental-health/" />
</svelte:head>

<article class="story-shell">
	<section class="hero">
		<div class="utility-row">
			<a href={`${base}/`}>{t().back}</a>
			<LanguageToggle />
		</div>
		<p class="kicker">{t().eyebrow}</p>
		<h1>{t().titleLead}<br /><em>{t().titleEm}</em></h1>
		<p class="dek">{t().dek}</p>

		<div class="hero-number" aria-label={t().heroLabel}>
			<strong>1.095</strong>
			<div>
				<span>billion</span>
				<p>{t().heroLabel}</p>
				<small>{t().heroDetail}</small>
			</div>
		</div>

		<div class="scroll-cue" aria-hidden="true">
			<i></i>
			<span>{t().scrollCue}</span>
		</div>
	</section>

	<GlobalMentalHealthScrolly />

	<section class="handoff">
		<p class="eyebrow">{t().transitionEyebrow}</p>
		<h2>{t().transitionTitle}</h2>
		<p>{t().transitionBody}</p>
	</section>

	<GlobalMentalHealthExplorer />

	<section class="method" aria-labelledby="method-title">
		<div class="method-head">
			<p class="eyebrow">{t().methodEyebrow}</p>
			<h2 id="method-title">{t().methodTitle}</h2>
		</div>
		<div class="method-grid">
			{#each t().methodCards as card, i}
				<article>
					<span>0{i + 1}</span>
					<h3>{card[0]}</h3>
					<p>{card[1]}</p>
				</article>
			{/each}
		</div>
	</section>

	<section class="sources" aria-labelledby="sources-title">
		<div>
			<p class="eyebrow">{t().sourcesEyebrow}</p>
			<h2 id="sources-title">{t().sourcesTitle}</h2>
			<p class="source-intro">{t().sourceNote}</p>
		</div>
		<div class="source-list">
			<a href={source('who-world-mental-health-2025').url} target="_blank" rel="noreferrer"><span>01</span>{source('who-world-mental-health-2025').label}<b>↗</b></a>
			<a href={source('who-mental-health-atlas-2024').url} target="_blank" rel="noreferrer"><span>02</span>{source('who-mental-health-atlas-2024').label}<b>↗</b></a>
			<a href={source('ihme-gbd-2021-mental-disorders').url} target="_blank" rel="noreferrer"><span>03</span>{source('ihme-gbd-2021-mental-disorders').label}<b>↗</b></a>
			<a href={source('plos-mdd-treatment-gap').url} target="_blank" rel="noreferrer"><span>04</span>{source('plos-mdd-treatment-gap').label}<b>↗</b></a>
		</div>
		<p class="atlas-note"><a href={`${base}/stories/global-mental-health/atlas`}>{t().standalone}</a></p>
	</section>

	<footer class="story-footer">
		<span>{facts.status}</span>
		<p>{t().status}</p>
	</footer>
</article>

<style>
	:global(body) {
		background: #f5f0e7;
		color: #171715;
	}

	.story-shell {
		--ink: #171715;
		--muted: #68645d;
		--paper: #f5f0e7;
		--panel: #fffaf2;
		--accent: #a33f32;
		--line: #d7cfc2;
		min-height: 100vh;
		background: var(--paper);
		color: var(--ink);
	}

	.hero,
	.handoff,
	.method,
	.sources,
	.story-footer {
		width: min(1180px, calc(100% - 40px));
		margin: 0 auto;
	}

	.hero {
		padding: clamp(2rem, 5vw, 4rem) 0 clamp(6rem, 11vw, 10rem);
	}

	.utility-row {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 1rem;
		margin-bottom: clamp(5rem, 10vw, 9rem);
		font: 700 0.78rem/1 var(--font-sans);
	}

	.utility-row > a {
		display: inline-flex;
		align-items: center;
		min-height: 44px;
		color: var(--ink);
		text-decoration: none;
	}

	.kicker,
	.eyebrow {
		font: 800 0.74rem/1.2 var(--font-mono);
		letter-spacing: 0.11em;
		text-transform: uppercase;
		color: var(--accent);
	}

	h1,
	h2,
	h3 {
		font-family: var(--font-serif);
	}

	h1 {
		max-width: 1080px;
		margin: 0.55rem 0 1.4rem;
		font-size: clamp(4.6rem, 12vw, 10.5rem);
		font-weight: 600;
		line-height: 0.82;
		letter-spacing: -0.07em;
	}

	h1 em {
		color: var(--accent);
		font-weight: 400;
	}

	.dek {
		max-width: 780px;
		margin: 0;
		font: 500 clamp(1.15rem, 2vw, 1.5rem)/1.6 var(--font-sans);
		color: var(--muted);
	}

	.hero-number {
		display: grid;
		grid-template-columns: minmax(0, 1.1fr) minmax(280px, 0.6fr);
		gap: 2rem;
		align-items: end;
		margin-top: clamp(5rem, 9vw, 8rem);
		padding-top: 2rem;
		border-top: 1px solid var(--line);
	}

	.hero-number > strong {
		font: 800 clamp(6rem, 18vw, 15rem)/0.72 var(--font-sans);
		letter-spacing: -0.08em;
		color: var(--accent);
	}

	.hero-number span,
	.hero-number p,
	.hero-number small {
		display: block;
	}

	.hero-number span {
		font: 800 clamp(2rem, 4vw, 3.5rem)/0.95 var(--font-sans);
		letter-spacing: -0.04em;
	}

	.hero-number p {
		margin: 0.8rem 0 0;
		font: 700 0.9rem/1.4 var(--font-sans);
	}

	.hero-number small {
		max-width: 46ch;
		margin-top: 0.7rem;
		font: 500 0.8rem/1.5 var(--font-sans);
		color: var(--muted);
	}

	.scroll-cue {
		display: flex;
		align-items: center;
		gap: 0.8rem;
		margin-top: 4rem;
		font: 650 0.76rem/1.35 var(--font-sans);
		color: var(--muted);
	}

	.scroll-cue i {
		position: relative;
		width: 1px;
		height: 44px;
		background: var(--ink);
	}

	.scroll-cue i::after {
		content: '';
		position: absolute;
		bottom: 0;
		left: -3px;
		width: 7px;
		height: 7px;
		border-right: 1px solid var(--ink);
		border-bottom: 1px solid var(--ink);
		transform: rotate(45deg);
	}

	.handoff {
		padding: clamp(7rem, 12vw, 12rem) 0;
		border-bottom: 1px solid var(--line);
	}

	.handoff h2,
	.method h2,
	.sources h2 {
		max-width: 1000px;
		margin: 0.55rem 0 1.2rem;
		font-size: clamp(3rem, 7vw, 6.7rem);
		font-weight: 600;
		line-height: 0.94;
		letter-spacing: -0.052em;
	}

	.handoff > p:last-child,
	.source-intro {
		max-width: 760px;
		margin: 0;
		font: 500 1.06rem/1.7 var(--font-sans);
		color: var(--muted);
	}

	.method {
		padding: clamp(7rem, 11vw, 10rem) 0;
		border-top: 1px solid var(--line);
	}

	.method-grid {
		display: grid;
		grid-template-columns: repeat(2, 1fr);
		margin-top: 4rem;
		border-top: 1px solid var(--line);
		border-left: 1px solid var(--line);
	}

	.method-grid article {
		padding: clamp(1.4rem, 3vw, 2.3rem);
		border-right: 1px solid var(--line);
		border-bottom: 1px solid var(--line);
		background: rgba(255, 250, 242, 0.5);
	}

	.method-grid span {
		font: 750 0.72rem/1 var(--font-mono);
		color: var(--accent);
	}

	.method-grid h3 {
		margin: 1.5rem 0 0.7rem;
		font-size: clamp(1.6rem, 3vw, 2.7rem);
		line-height: 1.05;
	}

	.method-grid p {
		margin: 0;
		font: 500 0.95rem/1.65 var(--font-sans);
		color: var(--muted);
	}

	.sources {
		display: grid;
		grid-template-columns: 0.85fr 1.15fr;
		gap: 5vw;
		padding: clamp(7rem, 11vw, 10rem) 0;
		border-top: 1px solid var(--line);
	}

	.sources h2 {
		font-size: clamp(2.7rem, 5vw, 5rem);
	}

	.source-list {
		border-top: 1px solid var(--line);
	}

	.source-list a {
		display: grid;
		grid-template-columns: 36px 1fr 24px;
		gap: 0.8rem;
		align-items: center;
		min-height: 68px;
		padding: 0.8rem 0;
		border-bottom: 1px solid var(--line);
		color: var(--ink);
		text-decoration: none;
		font: 650 0.86rem/1.45 var(--font-sans);
	}

	.source-list a:hover {
		color: var(--accent);
	}

	.source-list span {
		font: 700 0.68rem/1 var(--font-mono);
		color: var(--muted);
	}

	.source-list b {
		font-weight: 400;
		text-align: right;
	}

	.atlas-note {
		grid-column: 2;
		margin: 1.5rem 0 0;
	}

	.atlas-note a {
		font: 750 0.84rem/1.3 var(--font-sans);
		color: var(--accent);
	}

	.story-footer {
		display: flex;
		justify-content: space-between;
		gap: 2rem;
		padding: 2rem 0 4rem;
		border-top: 1px solid var(--line);
		font: 550 0.72rem/1.45 var(--font-sans);
		color: var(--muted);
	}

	.story-footer span {
		font-family: var(--font-mono);
	}

	.story-footer p {
		margin: 0;
		text-align: right;
	}

	@media (max-width: 760px) {
		.hero-number,
		.sources,
		.method-grid {
			grid-template-columns: 1fr;
		}

		.hero-number {
			gap: 1.4rem;
		}

		.method-grid {
			border-left: 0;
		}

		.method-grid article {
			border-left: 1px solid var(--line);
		}

		.atlas-note {
			grid-column: 1;
		}

		.story-footer {
			flex-direction: column;
		}

		.story-footer p {
			text-align: left;
		}
	}
</style>
