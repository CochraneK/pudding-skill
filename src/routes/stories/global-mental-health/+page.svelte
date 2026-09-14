<script>
	import { base } from '$app/paths';
	import facts from '$data/global-mental-health-facts.json';
	import LanguageToggle from '$components/LanguageToggle.svelte';
	import { language } from '$lib/language.js';

	const source = (id) => facts.sources[id];

	const copy = {
		zh: {
			back: '← 返回报告库',
			eyebrow: '全球精神健康 · 研究档案数据故事',
			titleLead: '世界的',
			titleEm: '隐形负担',
			dek: '超过 10 亿人生活在精神障碍之中。更尖锐的全球差距，不只是“哪里患病率高”，而是谁拥有足够的资金、专业人员与社区服务去回应需要。',
			sequenceEyebrow: '需求 → 公共优先级 → 照护能力',
			sequenceTitle: '同一个全球需求，落在完全不同的照护能力上。',
			needTitle: '需求是全球性的',
			needBody: '2021 年，WHO/GBD 估计约 10.95 亿人生活在精神障碍之中。13.6% 的年龄标化患病率意味着，这不是少数国家才面对的问题。',
			priorityTitle: '但公共预算中的位置仍然很小',
			priorityBody: '在报告数据的国家中，政府卫生支出分配给精神健康的全球中位数只有 2.1%。这不是“每个国家都花 2.1%”，而是报告国家分布的中位数。',
			capacityTitle: '真正拉开数量级的，是可用资源',
			capacityBody: 'WHO Mental Health Atlas 2024 报告：在有支出数据的收入组中，低收入国家政府精神健康人均支出中位数为 $0.04，高收入国家为 $65.89，约相差 1,647 倍。',
			lowIncome: '低收入国家中位数',
			highIncome: '高收入国家中位数',
			capacityCaveat: 'WHO Mental Health Atlas 2024 · 收入组中位数，基于报告国家。不同指标的报告覆盖并不相同，因此这不是国家排行榜。',
			secondaryEyebrow: '差距不只存在于钱',
			secondaryTitle: '预算只是照护能力的一层。',
			secondaryBody: '人员与真正获得治疗的机会也呈现明显差距。下面的数值来自不同证据体系，因此只用于说明“能力是多维的”，不把它们拼成一个虚假的综合排名。',
			workforceLabel: '全球专业精神健康工作人员中位数 / 每 10 万人',
			workforceNote: 'WHO 同时报告：低收入和中低收入环境约为 1.1–2.4，而高收入环境约为 67.2。',
			serviceLabel: '重度抑郁症病例中，模型估计使用精神健康服务',
			serviceNote: '系统综述/元回归：低/中低收入地区约 8%，高收入地区约 33%；低资源环境证据较稀疏。',
			adequateLabel: '重度抑郁症病例中，模型估计获得最低充分治疗',
			adequateNote: '同一研究估计：低/中低收入地区约 3%，高收入地区约 23%，不确定区间很宽。',
			depthEyebrow: '可选深挖，而不是理解前提',
			depthTitle: '想比较国家、年份和缺失数据？再进入 Capacity Atlas。',
			depthBody: '主论点已经在上面的静态证据中完整成立。国家探索器被保留为第二层：只有当你想回答“某个国家报告了什么、哪一年、缺了什么”时才需要打开。',
			depthLink: '打开独立 Capacity Atlas →',
			methodEyebrow: '避免虚假的确定性',
			methodTitle: '这些比较描述系统能力，不给国家贴“心理健康好坏”的标签。',
			methodCards: [
				['患病率 ≠ 诊断率', 'GBD/WHO 的患病率是模型估计，不是已诊断病例登记，也不是国家幸福度评分。'],
				['缺失 ≠ 0', 'WHO 指标覆盖率不同。没有报告的数据不能用 0 或插值偷偷补齐。'],
				['年份必须一起看', '不同 Atlas/GHO 指标可能来自不同报告轮次。跨国比较前必须同时阅读年份。'],
				['相关 ≠ 因果', '需求高、资源少可能同时出现，但这里的比较不能证明资源不足造成了某个患病率。']
			],
			sourcesEyebrow: '来源与证据链',
			sourcesTitle: '每个关键数字都能追溯回原始来源。',
			sourceNote: '报告中的数字来自 WHO、IHME/GBD 与同行评议研究。完整的 source ledger、numeric evidence 和 data-acquisition plan 保存在仓库的 Research Dossier 中。',
			status: '研究支持的静态优先数据故事 · 核心结论无需滚动状态或控件即可理解'
		},
		en: {
			back: '← Back to report library',
			eyebrow: 'GLOBAL MENTAL HEALTH · RESEARCH DOSSIER STORY',
			titleLead: "The world's",
			titleEm: 'invisible burden',
			dek: 'More than a billion people live with mental disorders. The sharper global divide is not simply where prevalence is higher, but whether care systems have the money, people and community services to respond.',
			sequenceEyebrow: 'NEED → PUBLIC PRIORITY → CARE CAPACITY',
			sequenceTitle: 'The same global need lands in radically different care systems.',
			needTitle: 'Need is global',
			needBody: 'In 2021, WHO/GBD estimated that about 1.095 billion people were living with a mental disorder. An age-standardized prevalence of 13.6% makes this a shared global problem, not one confined to a few countries.',
			priorityTitle: 'Yet mental health remains a small public-budget priority',
			priorityBody: 'Among reporting countries, the global median share of government health expenditure allocated to mental health was 2.1%. That is a median across reporters, not a claim that every country spends 2.1%.',
			capacityTitle: 'Available resources are where the orders of magnitude appear',
			capacityBody: 'WHO Mental Health Atlas 2024 reports a median of $0.04 per person in low-income countries and $65.89 in high-income countries among income groups with expenditure data — an approximate 1,647× gap.',
			lowIncome: 'Low-income median',
			highIncome: 'High-income median',
			capacityCaveat: 'WHO Mental Health Atlas 2024 · income-group medians among reporting countries. Reporting coverage differs by indicator, so this is not a country ranking.',
			secondaryEyebrow: 'THE GAP IS NOT ONLY MONEY',
			secondaryTitle: 'Spending is only one layer of care capacity.',
			secondaryBody: 'Workforce and the chance of actually receiving treatment also differ sharply. These figures come from different evidence systems, so they are shown as separate lenses rather than collapsed into a false composite ranking.',
			workforceLabel: 'specialized mental-health workers per 100,000 · global median',
			workforceNote: 'WHO also reports roughly 1.1–2.4 per 100,000 in low/lower-middle-income settings versus 67.2 in high-income settings.',
			serviceLabel: 'modeled mental-health service use among major-depression cases',
			serviceNote: 'Systematic review/meta-regression: about 8% in low/lower-middle-income locations versus 33% in high-income locations; low-resource evidence was sparse.',
			adequateLabel: 'modeled minimally adequate treatment among major-depression cases',
			adequateNote: 'The same study estimated about 3% in low/lower-middle-income locations versus 23% in high-income locations, with wide uncertainty intervals.',
			depthEyebrow: 'OPTIONAL DEPTH, NOT A PREREQUISITE',
			depthTitle: 'Want country, year and missingness detail? Open the Capacity Atlas next.',
			depthBody: 'The main argument is complete in the static evidence above. The country explorer remains a second layer only for readers asking what a specific country reported, in which year, and what is missing.',
			depthLink: 'Open the standalone Capacity Atlas →',
			methodEyebrow: 'AVOID FALSE CERTAINTY',
			methodTitle: 'These comparisons describe system capacity. They do not rank countries by “mental health.”',
			methodCards: [
				['Prevalence ≠ diagnosis', 'GBD/WHO prevalence is modeled evidence, not a registry of diagnosed cases and not a national wellbeing score.'],
				['Missing ≠ zero', 'WHO indicator coverage differs. Missing observations cannot be silently turned into zero or imputed away.'],
				['Read the year', 'Atlas/GHO indicators can come from different reporting rounds. Read reporting year before comparing countries.'],
				['Association ≠ causation', 'High need and low capacity can coexist, but these comparisons cannot prove that resource scarcity caused a prevalence level.']
			],
			sourcesEyebrow: 'SOURCES + PROVENANCE',
			sourcesTitle: 'Every material number can be traced back to its source.',
			sourceNote: 'The story uses WHO, IHME/GBD, and peer-reviewed evidence. The repository keeps the full source ledger, numeric evidence table, and data-acquisition plan in the Research Dossier.',
			status: 'Research-backed static-first data story · the core conclusion requires no scroll state or control'
		}
	};

	const t = () => copy[$language];
</script>

<svelte:head>
	<title>{t().titleLead} {t().titleEm} · pudding-skill</title>
	<meta name="description" content={t().dek} />
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
	</section>

	<section class="sequence-intro">
		<p class="eyebrow">{t().sequenceEyebrow}</p>
		<h2>{t().sequenceTitle}</h2>
	</section>

	<section
		class="static-sequence"
		data-production-winner="static-gap-atlas"
		data-primary-interaction="none"
		data-borrowed-from="care-capacity-ladder"
	>
		<article class="beat need" data-story-beat="need" data-claim-id="need-scale">
			<div class="beat-index">01</div>
			<div class="beat-copy">
				<p class="eyebrow">{t().needTitle}</p>
				<h2>1.095 <em>billion</em></h2>
				<p>{t().needBody}</p>
				<strong class="support-number">13.6%</strong>
			</div>
		</article>

		<article class="beat priority" data-story-beat="priority" data-claim-id="public-priority">
			<div class="beat-index">02</div>
			<div class="beat-copy">
				<p class="eyebrow">{t().priorityTitle}</p>
				<h2>2.1%</h2>
				<p>{t().priorityBody}</p>
			</div>
		</article>

		<article class="beat capacity" data-story-beat="capacity" data-claim-id="spending-gap">
			<div class="beat-index">03</div>
			<div class="beat-copy">
				<p class="eyebrow">{t().capacityTitle}</p>
				<h2>1,647×</h2>
				<p>{t().capacityBody}</p>

				<div class="gap-bars" role="img" aria-label="$0.04 low-income median versus $65.89 high-income median government mental-health spending per person">
					<div class="gap-row low">
						<div class="gap-label"><span>{t().lowIncome}</span><strong>$0.04</strong></div>
						<div class="track"><i></i></div>
					</div>
					<div class="gap-row high">
						<div class="gap-label"><span>{t().highIncome}</span><strong>$65.89</strong></div>
						<div class="track"><i></i></div>
					</div>
				</div>
				<p class="caveat">{t().capacityCaveat}</p>
			</div>
		</article>
	</section>

	<section class="secondary-evidence">
		<div class="section-head">
			<p class="eyebrow">{t().secondaryEyebrow}</p>
			<h2>{t().secondaryTitle}</h2>
			<p>{t().secondaryBody}</p>
		</div>
		<div class="evidence-grid">
			<article>
				<strong>13.5</strong>
				<h3>{t().workforceLabel}</h3>
				<p>{t().workforceNote}</p>
			</article>
			<article>
				<strong>8% → 33%</strong>
				<h3>{t().serviceLabel}</h3>
				<p>{t().serviceNote}</p>
			</article>
			<article>
				<strong>3% → 23%</strong>
				<h3>{t().adequateLabel}</h3>
				<p>{t().adequateNote}</p>
			</article>
		</div>
	</section>

	<section class="optional-depth" data-optional-depth="country-capacity-explorer">
		<div>
			<p class="eyebrow">{t().depthEyebrow}</p>
			<h2>{t().depthTitle}</h2>
			<p>{t().depthBody}</p>
		</div>
		<a class="depth-link" href={`${base}/stories/global-mental-health/atlas`}>{t().depthLink}</a>
	</section>

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
	.sequence-intro,
	.static-sequence,
	.secondary-evidence,
	.optional-depth,
	.method,
	.sources,
	.story-footer {
		width: min(1180px, calc(100% - 40px));
		margin: 0 auto;
	}

	.hero {
		padding: clamp(2rem, 5vw, 4rem) 0 clamp(7rem, 12vw, 11rem);
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

	.sequence-intro {
		padding: clamp(4rem, 8vw, 7rem) 0 2.5rem;
		border-top: 1px solid var(--line);
	}

	.sequence-intro h2,
	.section-head h2,
	.optional-depth h2,
	.method h2,
	.sources h2 {
		max-width: 1000px;
		margin: 0.55rem 0 1.2rem;
		font-size: clamp(2.8rem, 7vw, 6.5rem);
		font-weight: 600;
		line-height: 0.94;
		letter-spacing: -0.052em;
	}

	.static-sequence {
		border-top: 1px solid var(--line);
	}

	.beat {
		display: grid;
		grid-template-columns: 90px minmax(0, 1fr);
		gap: clamp(1.5rem, 5vw, 5rem);
		padding: clamp(4rem, 8vw, 7rem) 0;
		border-bottom: 1px solid var(--line);
	}

	.beat-index {
		padding-top: 0.5rem;
		font: 750 0.78rem/1 var(--font-mono);
		color: var(--muted);
	}

	.beat-copy {
		max-width: 900px;
	}

	.beat-copy h2 {
		margin: 0.7rem 0 1rem;
		font-size: clamp(4.6rem, 12vw, 10rem);
		font-weight: 650;
		line-height: 0.82;
		letter-spacing: -0.065em;
	}

	.beat-copy h2 em {
		font-size: 0.36em;
		font-style: normal;
		letter-spacing: -0.03em;
		color: var(--muted);
	}

	.beat-copy > p:not(.eyebrow):not(.caveat) {
		max-width: 720px;
		margin: 0;
		font: 500 1.04rem/1.7 var(--font-sans);
		color: var(--muted);
	}

	.support-number {
		display: inline-block;
		margin-top: 2rem;
		padding: 0.65rem 0.9rem;
		border: 1px solid var(--line);
		border-radius: 999px;
		font: 800 1rem/1 var(--font-mono);
	}

	.gap-bars {
		display: grid;
		gap: 1.5rem;
		margin-top: 3rem;
		padding: clamp(1.3rem, 3vw, 2rem);
		border: 1px solid var(--line);
		border-radius: 16px;
		background: var(--panel);
	}

	.gap-label {
		display: flex;
		align-items: baseline;
		justify-content: space-between;
		gap: 1rem;
		margin-bottom: 0.55rem;
		font: 650 0.88rem/1.35 var(--font-sans);
	}

	.gap-label strong {
		font: 800 1.15rem/1 var(--font-mono);
	}

	.track {
		height: 12px;
		overflow: hidden;
		border-radius: 999px;
		background: #e4ddd2;
	}

	.track i {
		display: block;
		height: 100%;
		border-radius: inherit;
		background: var(--accent);
	}

	.gap-row.low .track i {
		width: 1.5%;
	}

	.gap-row.high .track i {
		width: 100%;
	}

	.caveat {
		max-width: 760px;
		margin: 1.2rem 0 0;
		font: 500 0.8rem/1.6 var(--font-sans);
		color: var(--muted);
	}

	.secondary-evidence {
		padding: clamp(7rem, 11vw, 10rem) 0;
	}

	.section-head > p:last-child,
	.optional-depth > div > p:last-child,
	.source-intro {
		max-width: 760px;
		margin: 0;
		font: 500 1.02rem/1.7 var(--font-sans);
		color: var(--muted);
	}

	.evidence-grid {
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		margin-top: 4rem;
		border-top: 1px solid var(--line);
		border-left: 1px solid var(--line);
	}

	.evidence-grid article {
		padding: clamp(1.4rem, 3vw, 2.2rem);
		border-right: 1px solid var(--line);
		border-bottom: 1px solid var(--line);
		background: rgba(255, 250, 242, 0.5);
	}

	.evidence-grid strong {
		display: block;
		font: 750 clamp(2.4rem, 5vw, 4.5rem)/0.95 var(--font-serif);
		letter-spacing: -0.045em;
		color: var(--accent);
	}

	.evidence-grid h3 {
		margin: 1.5rem 0 0.8rem;
		font-size: clamp(1.35rem, 2.4vw, 2.15rem);
		line-height: 1.08;
	}

	.evidence-grid p {
		margin: 0;
		font: 500 0.9rem/1.6 var(--font-sans);
		color: var(--muted);
	}

	.optional-depth {
		display: grid;
		grid-template-columns: minmax(0, 1fr) minmax(220px, 0.34fr);
		gap: 4vw;
		align-items: end;
		padding: clamp(5rem, 9vw, 8rem) 0;
		border-top: 1px solid var(--line);
		border-bottom: 1px solid var(--line);
	}

	.optional-depth h2 {
		font-size: clamp(2.5rem, 5vw, 4.8rem);
	}

	.depth-link {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		min-height: 54px;
		padding: 0.9rem 1.2rem;
		border: 1px solid var(--ink);
		border-radius: 999px;
		color: var(--ink);
		font: 750 0.85rem/1.2 var(--font-sans);
		text-decoration: none;
	}

	.depth-link:hover {
		background: var(--ink);
		color: var(--paper);
	}

	.method {
		padding: clamp(7rem, 11vw, 10rem) 0;
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
		.beat,
		.evidence-grid,
		.optional-depth,
		.method-grid,
		.sources {
			grid-template-columns: 1fr;
		}

		.beat {
			gap: 1.2rem;
		}

		.evidence-grid,
		.method-grid {
			border-left: 0;
		}

		.evidence-grid article,
		.method-grid article {
			border-left: 1px solid var(--line);
		}

		.optional-depth {
			align-items: start;
		}

		.depth-link {
			justify-self: start;
		}

		.story-footer {
			flex-direction: column;
		}

		.story-footer p {
			text-align: left;
		}
	}
</style>
