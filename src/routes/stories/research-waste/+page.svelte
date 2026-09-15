<script>
	import { onMount } from 'svelte';
	import { base } from '$app/paths';
	import facts from '$data/research-waste-facts.json';
	import LanguageToggle from '$components/LanguageToggle.svelte';
	import ScrollyShell from '$components/ScrollyShell.svelte';
	import { language } from '$lib/language.js';

	const observed2023 = facts.observed_publications['2023'];
	const pubGrowth = facts.publication_growth_cagr_2010_2023;
	const secondsPerYear = 365.2425 * 24 * 60 * 60;
	const annualForYear = (year) => observed2023 * Math.pow(1 + pubGrowth, year - 2023);
	const crossingYear = (baseYear, publications, retractions, retractionGrowth) => {
		const relative = (1 + retractionGrowth) / (1 + pubGrowth);
		if (relative <= 1) return Infinity;
		return baseYear + Math.log(publications / retractions) / Math.log(relative);
	};

	const longCross = Math.round(
		crossingYear(
			2021,
			facts.observed_publications['2021'],
			facts.retraction_anchors['2021'],
			facts.retraction_growth_cagr_2010_2021
		)
	);
	const spikeCross = Math.round(
		crossingYear(
			2023,
			observed2023,
			facts.retraction_anchors['2023_minimum'],
			facts.retraction_growth_cagr_2010_2023_spike_inclusive
		)
	);
	const hiddenCriterionPapers = Math.round(observed2023 * facts.estimated_retraction_criterion_share);
	const reviewerFteYears = Math.round(facts.peer_review_hours_2020 / 2000);
	const millionDollarGrants = Math.round(facts.irreproducible_preclinical_cost_usd / 1_000_000);
	const postRetractionUnacknowledged = 1 - facts.post_retraction_acknowledgement_share;

	let currentYear = $state(2026);
	let modeledAnnual = $state(annualForYear(currentYear));
	let todayCount = $state(0);
	let yearCountAtOpen = $state(0);
	let sinceOpen = $state(0);
	let openedAt = $state(0);
	let papersPerDay = $state(5);
	let readingYears = $state(50);
	let scenario = $state('long');
	let pagesPerPaper = $state(10);
	let printCopies = $state(1);
	let deviceWhPerPaper = $state(60);
	let scrollProgress = $state(0);

	let perSecond = $derived(modeledAnnual / secondsPerYear);
	let perDay = $derived(modeledAnnual / 365.2425);
	let secondsPerPaper = $derived(1 / perSecond);
	let annualRead = $derived(papersPerDay * 365.2425);
	let annualShare = $derived((annualRead / modeledAnnual) * 100);
	let lifetimeRead = $derived(annualRead * readingYears);
	let lifetimeVsOneYear = $derived((lifetimeRead / modeledAnnual) * 100);
	let worldDuringReadingYears = $derived(modeledAnnual * readingYears);
	let activeCross = $derived(scenario === 'long' ? longCross : spikeCross);
	let activeRetGrowth = $derived(
		scenario === 'long'
			? facts.retraction_growth_cagr_2010_2021
			: facts.retraction_growth_cagr_2010_2023_spike_inclusive
	);
	let paperKg = $derived(
		(facts.retraction_anchors['2023_minimum'] * pagesPerPaper * printCopies * 5) / 1000
	);
	let deviceKwh = $derived(
		(facts.retraction_anchors['2023_minimum'] * deviceWhPerPaper) / 1000
	);

	const fmt = (n, digits = 0) =>
		new Intl.NumberFormat($language === 'zh' ? 'zh-CN' : 'en-US', {
			maximumFractionDigits: digits
		}).format(n);
	const pct = (n, digits = 2) => `${fmt(n, digits)}%`;

	const copy = {
		zh: {
			back: '← 返回报告库',
			eyebrow: '研究浪费 · 科研诚信 · 论文洪水',
			titleLead: '我们发表得比',
			titleEm: '任何人能读的都快',
			dek: '这不是一个“垃圾论文占多少”的简单故事。它追问的是：论文生产线有多快、错误和低价值研究如何漏过筛选、撤稿之后污染为何仍会传播，以及人类把多少时间和资源交给了这个系统。',
			scrollCue: '向下滚动 · 同一张舞台，七次换证据',
			model: '节奏模型，不是实时数据库',
			openSince: '从你打开页面以来',
			papers: '篇',
			statusObserved: 'OBSERVED · 观察值',
			statusEstimate: 'LITERATURE ESTIMATE · 文献估计',
			statusDerived: 'DERIVED · 派生计算',
			statusScenario: 'SCENARIO · 情景外推',
			statusAssumption: 'ASSUMPTION · 假设',
			steps: {
				volume: {
					kicker: '01 · 论文洪水',
					title: '先感受这台机器的速度。',
					body: '2023 年，Scopus 收录的全球科学与工程论文约 327.5 万篇。把 2010–2023 的历史增速机械延长到当前年份，模型约为 367 万篇/年——平均每 8.6 秒又多一篇。',
					note: '今天、今年、打开页面以来的数字都是节奏模型，不是实时抓取论文数据库。'
				},
				reading: {
					kicker: '02 · 一个人读不完',
					title: '一天读 N 篇，一辈子仍只碰到知识海洋的一小层。',
					body: '把你的阅读速度放进同一台生产线：你可以读得更勤奋，但个人吞吐量和全球发表量根本不在一个数量级。',
					daily: '每天完整读',
					years: '持续阅读年数'
				},
				boundary: {
					kicker: '03 · 先把词拆开',
					title: '“无用学术”不是一个可直接统计的变量。',
					body: '撤稿、造假、不可重复、论文工厂、低价值研究会重叠，但不是同义词。把它们揉成一个“垃圾论文率”，本身就是坏统计。'
				},
				hidden: {
					kicker: '04 · 冰山',
					title: '被正式撤稿的，只是可见的表层。',
					body: '一篇 Nature 评论曾给出约 1/50 论文可能符合至少一项 COPE 撤稿标准的数量级估计。机械套到 2023 年产量，是约 6.55 万篇；它不是“6.55 万篇造假论文”，也不能直接减去 2023 年撤稿数。'
				},
				contamination: {
					kicker: '05 · 污染会继续走',
					title: '撤稿按钮，不会自动切断知识传播。',
					body: '一项数据库级研究分析 13,252 个撤稿后引用语境，只有 722 个——5.4%——明确提到被引论文已经撤稿。其余引用不全等于误用，但说明“已撤稿”并不会自动从下游研究里消失。'
				},
				cost: {
					kicker: '06 · 最贵的是人和机会',
					title: '真正昂贵的不是 PDF，而是注意力和研发资源。',
					body: '2020 年全球同行评审被估计投入超过 1 亿小时；按 2,000 小时一个全职研究年，约等于 5 万个 FTE 年。另一项研究估计，美国临床前生命科学每年约 280 亿美元与不可重复研究相关。两者都不是“全球学术浪费总额”。'
				},
				crossing: {
					kicker: '07 · 恐怖交叉点',
					title: '“撤稿何时跑赢发表？”答案可以被你的假设移动 17 年。',
					body: '用 2010→2021 的撤稿增速机械外推，交叉点约在 2071；把 2023 年 Hindawi 集中清理造成的异常高峰也当成永久趋势，交叉点会被提前到约 2054。这个差异比任一单独年份更重要。',
					long: '长期窗口 · 2071',
					spike: '含 2023 高峰 · 2054'
				}
			},
			boundaryCards: [
				['已撤稿', '正式撤回的可观察子集；撤稿也可能来自诚实错误。', 'OBSERVED'],
				['应撤未撤', '“约 1/50”是撤稿标准的风险数量级，不是已证实造假。', 'LITERATURE ESTIMATE'],
				['不可重复', '无法可靠重现的原因很多，并不自动等于故意不端。', 'LITERATURE ESTIMATE'],
				['低价值研究', '“重要不重要”依赖领域和目的，没有可信的全球统一无用率。', 'VALUE JUDGMENT']
			],
			labEyebrow: '假设实验室',
			labTitle: '纸张、电费可以算，但只能当透明情景。',
			labDek: '这些物理成本不是主结论。保留它们，是为了示范：当没有直接测量时，把假设放在滑块上，而不是藏在一句确定性很强的话里。',
			pagesPerPaper: '每篇打印页数',
			printCopies: '每篇打印份数',
			deviceWh: '每篇数字阅读耗电（Wh）',
			paperResult: '按 10,000 篇撤稿论文计算，纸张情景约',
			energyResult: '数字阅读情景约',
			kg: 'kg 纸',
			kwh: 'kWh',
			closeEyebrow: '真正的危机不是某个年份',
			closeTitle: '当生产、检查和纠错的速度长期失衡，知识系统会背上复利式的质量债。',
			closeBody: '所以不要把 2054 或 2071 当预言。更值得监测的是：论文产量、撤稿与纠错能力、同行评审负荷、论文工厂渗透率，以及错误被下游继续使用的时间。',
			sources: '来源与边界',
			sourcesDek: '观察值、文献估计、派生计算和情景外推在页面中分开标注。来源保留原始链接与限定条件。'
		},
		en: {
			back: '← Back to report library',
			eyebrow: 'RESEARCH WASTE · INTEGRITY · PUBLICATION FLOOD',
			titleLead: 'We publish faster than',
			titleEm: 'any person can read',
			dek: 'This is not a simple story about a universal “junk-paper rate.” It asks how fast the publication machine runs, how errors and low-value work pass through filters, why contamination continues after retraction, and how much human attention the system consumes.',
			scrollCue: 'Scroll · one stage, seven evidence states',
			model: 'Pace model, not a live literature database',
			openSince: 'Since you opened this page',
			papers: 'papers',
			statusObserved: 'OBSERVED',
			statusEstimate: 'LITERATURE ESTIMATE',
			statusDerived: 'DERIVED',
			statusScenario: 'SCENARIO',
			statusAssumption: 'ASSUMPTION',
			steps: {
				volume: {
					kicker: '01 · THE FLOOD',
					title: 'First, feel the speed of the machine.',
					body: 'Scopus indexed about 3.275 million science and engineering papers worldwide in 2023. Extending the 2010–2023 historical growth rate mechanically to the current year gives roughly 3.67 million a year — about one paper every 8.6 seconds.',
					note: 'Today, this year and since-open counts are a pace model, not a live query of publication databases.'
				},
				reading: {
					kicker: '02 · ONE READER',
					title: 'Read N papers a day and a lifetime still reaches only a thin layer.',
					body: 'Put your reading speed against the same production line. You can read harder, but an individual and the global publication system operate at fundamentally different scales.',
					daily: 'Full papers per day',
					years: 'Reading-career years'
				},
				boundary: {
					kicker: '03 · SEPARATE THE TERMS',
					title: '“Useless research” is not a directly countable variable.',
					body: 'Retractions, fraud, irreproducibility, paper mills and low-value research overlap, but they are not synonyms. Compressing them into one global junk-paper percentage would itself be bad statistics.'
				},
				hidden: {
					kicker: '04 · THE ICEBERG',
					title: 'Formally retracted papers are only the visible layer.',
					body: 'A Nature commentary offered a rough estimate that about 1 in 50 papers might meet at least one COPE retraction criterion. Applying 2% mechanically to 2023 output gives about 65,500 papers. That is not “65,500 fraudulent papers,” and it cannot simply be subtracted from 2023 retractions.'
				},
				contamination: {
					kicker: '05 · CONTAMINATION TRAVELS',
					title: 'A retraction button does not automatically cut the knowledge chain.',
					body: 'A database-scale study examined 13,252 post-retraction citation contexts. Only 722 — 5.4% — explicitly acknowledged that the cited paper had been retracted. The rest are not all misuse, but retraction status clearly does not erase downstream use.'
				},
				cost: {
					kicker: '06 · PEOPLE + OPPORTUNITY',
					title: 'The expensive part is not the PDF. It is attention and research capacity.',
					body: 'Global peer review was estimated to consume more than 100 million hours in 2020 — roughly 50,000 full-time research years at 2,000 hours each. A separate study estimated about $28B/year associated with irreproducible US preclinical life-science research. Neither number is a global total of wasted science.'
				},
				crossing: {
					kicker: '07 · THE SCARY CROSSING',
					title: '“When do retractions overtake publications?” can move 17 years with one assumption.',
					body: 'Mechanically extending 2010→2021 retraction growth yields a crossing around 2071. Treating the exceptional 2023 Hindawi cleanup spike as permanent growth pulls it forward to about 2054. The instability of the date is the point.',
					long: 'Longer window · 2071',
					spike: 'Include 2023 spike · 2054'
				}
			},
			boundaryCards: [
				['Retracted', 'The formally withdrawn subset; retractions can also follow honest error.', 'OBSERVED'],
				['Retractable but not retracted', '“About 1 in 50” is a risk-scale estimate, not confirmed fraud.', 'LITERATURE ESTIMATE'],
				['Irreproducible', 'Many causes can prevent reliable replication; intent is not implied.', 'LITERATURE ESTIMATE'],
				['Low value', 'Importance depends on domain and purpose; there is no credible universal global rate.', 'VALUE JUDGMENT']
			],
			labEyebrow: 'ASSUMPTION LAB',
			labTitle: 'Paper and electricity can be modeled — but only as transparent scenarios.',
			labDek: 'These physical costs are not the central claim. The controls demonstrate a rule: when direct measurement is missing, expose assumptions instead of hiding them inside a confident sentence.',
			pagesPerPaper: 'Printed pages per paper',
			printCopies: 'Printed copies per paper',
			deviceWh: 'Digital-reading energy per paper (Wh)',
			paperResult: 'For 10,000 retracted papers, the paper scenario is about',
			energyResult: 'The digital-reading scenario is about',
			kg: 'kg paper',
			kwh: 'kWh',
			closeEyebrow: 'THE CRISIS IS NOT ONE DATE',
			closeTitle: 'When production, checking and correction remain out of balance, the knowledge system accumulates compounding quality debt.',
			closeBody: 'So do not treat 2054 or 2071 as predictions. Watch the rates that generate the risk: publication output, correction capacity, peer-review load, paper-mill penetration and how long retracted work remains active downstream.',
			sources: 'Sources + boundaries',
			sourcesDek: 'Observed values, literature estimates, derived calculations and scenarios are labeled separately. Source links retain their original scope and limitations.'
		}
	};

	const t = () => copy[$language];
	const stepData = () => [
		{ id: 'volume', status: t().statusObserved, ...t().steps.volume },
		{ id: 'reading', status: t().statusDerived, ...t().steps.reading },
		{ id: 'boundary', status: t().statusEstimate, ...t().steps.boundary },
		{ id: 'hidden', status: t().statusEstimate, ...t().steps.hidden },
		{ id: 'contamination', status: t().statusObserved, ...t().steps.contamination },
		{ id: 'cost', status: t().statusEstimate, ...t().steps.cost },
		{ id: 'crossing', status: t().statusScenario, ...t().steps.crossing }
	];

	onMount(() => {
		const opened = new Date();
		openedAt = opened.getTime();
		currentYear = opened.getFullYear();
		modeledAnnual = annualForYear(currentYear);
		const startOfYear = new Date(opened.getFullYear(), 0, 1).getTime();
		yearCountAtOpen = ((openedAt - startOfYear) / 1000) * (modeledAnnual / secondsPerYear);

		const tick = () => {
			const now = new Date();
			const startOfDay = new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime();
			todayCount = ((now.getTime() - startOfDay) / 1000) * (modeledAnnual / secondsPerYear);
			sinceOpen = ((now.getTime() - openedAt) / 1000) * (modeledAnnual / secondsPerYear);
		};
		const updateProgress = () => {
			const root = document.documentElement;
			const distance = Math.max(1, root.scrollHeight - root.clientHeight);
			scrollProgress = Math.min(1, Math.max(0, root.scrollTop / distance));
		};
		tick();
		updateProgress();
		const timer = window.setInterval(tick, 1000);
		window.addEventListener('scroll', updateProgress, { passive: true });
		window.addEventListener('resize', updateProgress);
		return () => {
			window.clearInterval(timer);
			window.removeEventListener('scroll', updateProgress);
			window.removeEventListener('resize', updateProgress);
		};
	});
</script>

<svelte:head>
	<title>{t().titleLead} {t().titleEm} · pudding-skill</title>
	<meta name="description" content={t().dek} />
	<meta property="og:title" content={`${t().titleLead} ${t().titleEm}`} />
	<meta property="og:description" content={t().dek} />
	<meta name="theme-color" content="#10151d" />
	<link rel="canonical" href="https://cochranek.github.io/pudding-skill/stories/research-waste/" />
</svelte:head>

<div class="progress" aria-hidden="true"><i style={`transform:scaleX(${scrollProgress})`}></i></div>

<article class="story">
	<header class="hero">
		<div class="utility">
			<a href={`${base}/`}>{t().back}</a>
			<LanguageToggle />
		</div>
		<div class="hero-inner">
			<p class="eyebrow">{t().eyebrow}</p>
			<h1>{t().titleLead}<br /><em>{t().titleEm}</em></h1>
			<p class="dek">{t().dek}</p>
			<div class="hero-meter">
				<strong>{fmt(modeledAnnual / 1_000_000, 2)}M</strong>
				<span>{t().papers} / {currentYear}</span>
			</div>
			<div class="ticker" aria-live="off">
				<span class="live-dot"></span>
				{t().openSince} <b>{fmt(sinceOpen)}</b> {t().papers}
			</div>
			<p class="scroll-cue">↓ {t().scrollCue}</p>
		</div>
	</header>

	{#snippet graphic(item)}
		<div class={`viz-card viz-${item?.id ?? 'none'}`} data-research-waste-state={item?.id}>
			<p class="viz-status">{item?.status}</p>

			{#if item?.id === 'volume'}
				<p class="viz-kicker">{t().model}</p>
				<div class="giant-number">{fmt(modeledAnnual)}</div>
				<p class="viz-unit">{t().papers} / {currentYear}</p>
				<div class="metric-row">
					<div><strong>{fmt(perDay)}</strong><span>{t().papers} / day</span></div>
					<div><strong>{secondsPerPaper.toFixed(1)}s</strong><span>/ paper</span></div>
					<div><strong>{fmt(todayCount)}</strong><span>today</span></div>
				</div>
				<p class="small-note">2023 observed: {fmt(observed2023)} · modeled current-year pace</p>
			{:else if item?.id === 'reading'}
				<p class="viz-kicker">{papersPerDay} / day × {readingYears} years</p>
				<div class="giant-number">{pct(lifetimeVsOneYear, 1)}</div>
				<p class="viz-unit">of one current year of output</p>
				<div class="read-rail" aria-hidden="true">
					<i style={`width:${Math.min(100, lifetimeVsOneYear)}%`}></i>
				</div>
				<div class="metric-row">
					<div><strong>{fmt(lifetimeRead)}</strong><span>read in lifetime</span></div>
					<div><strong>{pct(annualShare, 3)}</strong><span>of annual output</span></div>
					<div><strong>{fmt(worldDuringReadingYears / 1_000_000, 0)}M</strong><span>produced meanwhile*</span></div>
				</div>
				<p class="small-note">*holding current output flat; no future growth assumed</p>
			{:else if item?.id === 'boundary'}
				<div class="boundary-grid">
					{#each t().boundaryCards as card}
						<div class="boundary-card">
							<small>{card[2]}</small>
							<strong>{card[0]}</strong>
							<p>{card[1]}</p>
						</div>
					{/each}
				</div>
			{:else if item?.id === 'hidden'}
				<div class="iceberg" aria-label="Observed 2023 retractions compared with a 2 percent criterion scenario">
					<div class="ice-tip">
						<strong>&gt;{fmt(facts.retraction_anchors['2023_minimum'])}</strong>
						<span>2023 retractions</span>
					</div>
					<div class="waterline"></div>
					<div class="ice-under">
						<strong>≈ {fmt(hiddenCriterionPapers)}</strong>
						<span>2% criterion scenario</span>
					</div>
				</div>
				<p class="small-note">Different publication cohorts + exceptional 2023 cleanup → do not subtract directly.</p>
			{:else if item?.id === 'contamination'}
				<p class="viz-kicker">13,252 post-retraction citation contexts</p>
				<div class="citation-bar" role="img" aria-label="5.4 percent acknowledged retraction, 94.6 percent did not explicitly acknowledge it">
					<div class="ack" style={`width:${facts.post_retraction_acknowledgement_share * 100}%`}></div>
					<div class="unack" style={`width:${postRetractionUnacknowledged * 100}%`}></div>
				</div>
				<div class="split-labels">
					<div><strong>5.4%</strong><span>explicitly acknowledged</span></div>
					<div><strong>94.6%</strong><span>did not explicitly acknowledge</span></div>
				</div>
				<div class="chain" aria-hidden="true">
					<span>paper</span><b>→</b><span>review</span><b>→</b><span>student</span><b>→</b><span>experiment</span><b>→</b><span>policy</span>
				</div>
			{:else if item?.id === 'cost'}
				<div class="cost-grid">
					<div class="cost-card">
						<small>peer review · 2020 estimate</small>
						<strong>&gt;100M</strong>
						<span>hours</span>
						<p>≈ {fmt(reviewerFteYears)} full-time research years</p>
					</div>
					<div class="cost-card">
						<small>US preclinical life science</small>
						<strong>$28B</strong>
						<span>/ year estimate</span>
						<p>capacity equivalent: {fmt(millionDollarGrants)} × $1M projects</p>
					</div>
				</div>
				<p class="small-note">Capacity equivalents are not predictions of social return.</p>
			{:else if item?.id === 'crossing'}
				<div class="crossing-years">
					<div class:active={scenario === 'long'}><small>2010→2021 window</small><strong>{longCross}</strong></div>
					<div class:active={scenario === 'spike'}><small>2010→2023 spike-inclusive</small><strong>{spikeCross}</strong></div>
				</div>
				<div class="timeline" aria-hidden="true">
					<i class="now"></i><i class="spike"></i><i class="long"></i>
					<span class="nlabel">2026</span><span class="slabel">2054</span><span class="llabel">2071</span>
				</div>
				<p class="scenario-result">Selected mechanical crossing: <strong>{activeCross}</strong> · retraction CAGR assumption {pct(activeRetGrowth * 100, 1)}</p>
			{/if}
		</div>
	{/snippet}

	{#snippet step(item)}
		<p class="step-kicker">{item.kicker}</p>
		<h2>{item.title}</h2>
		<p>{item.body}</p>
		{#if item.note}<p class="step-note">{item.note}</p>{/if}

		{#if item.id === 'reading'}
			<div class="controls">
				<label>
					<span>{item.daily}: <b>{papersPerDay}</b></span>
					<input aria-label={item.daily} type="range" min="1" max="20" step="1" bind:value={papersPerDay} />
				</label>
				<label>
					<span>{item.years}: <b>{readingYears}</b></span>
					<input aria-label={item.years} type="range" min="10" max="70" step="5" bind:value={readingYears} />
				</label>
			</div>
		{:else if item.id === 'crossing'}
			<div class="scenario-buttons" aria-label="Retraction growth scenario">
				<button class:active={scenario === 'long'} onclick={() => (scenario = 'long')}>{item.long}</button>
				<button class:active={scenario === 'spike'} onclick={() => (scenario = 'spike')}>{item.spike}</button>
			</div>
			<p class="step-note">Neither line is a forecast. Both are deliberately mechanical extrapolations.</p>
		{/if}
	{/snippet}

	<section class="scrolly-zone">
		<ScrollyShell steps={stepData()} {graphic} {step} />
	</section>

	<section class="lab-section">
		<div class="section-inner">
			<p class="eyebrow">{t().labEyebrow}</p>
			<h2>{t().labTitle}</h2>
			<p class="section-dek">{t().labDek}</p>

			<div class="lab-grid">
				<label>
					<span>{t().pagesPerPaper}</span>
					<input type="range" min="4" max="30" step="1" bind:value={pagesPerPaper} />
					<b>{pagesPerPaper}</b>
				</label>
				<label>
					<span>{t().printCopies}</span>
					<input type="range" min="0" max="5" step="1" bind:value={printCopies} />
					<b>{printCopies}</b>
				</label>
				<label>
					<span>{t().deviceWh}</span>
					<input type="range" min="10" max="200" step="10" bind:value={deviceWhPerPaper} />
					<b>{deviceWhPerPaper}</b>
				</label>
			</div>

			<div class="lab-results">
				<article>
					<p>{t().paperResult}</p>
					<strong>{fmt(paperKg)} {t().kg}</strong>
					<small>{t().statusAssumption}</small>
				</article>
				<article>
					<p>{t().energyResult}</p>
					<strong>{fmt(deviceKwh)} {t().kwh}</strong>
					<small>{t().statusAssumption}</small>
				</article>
			</div>
		</div>
	</section>

	<section class="closing">
		<div class="section-inner narrow">
			<p class="eyebrow">{t().closeEyebrow}</p>
			<h2>{t().closeTitle}</h2>
			<p>{t().closeBody}</p>
			<div class="closing-numbers">
				<span><b>{spikeCross}</b> spike-inclusive scenario</span>
				<span><b>{longCross}</b> longer-window scenario</span>
				<span><b>17</b> years moved by one growth window</span>
			</div>
		</div>
	</section>

	<section class="sources">
		<div class="section-inner">
			<p class="eyebrow">{t().sources}</p>
			<h2>{t().sources}</h2>
			<p class="section-dek">{t().sourcesDek}</p>
			<div class="source-list">
				{#each facts.sources as source, index}
					<article>
						<span>{String(index + 1).padStart(2, '0')}</span>
						<div>
							<a href={source.url} target="_blank" rel="noreferrer">{source.label}</a>
							<p>{source.note}</p>
						</div>
					</article>
				{/each}
			</div>
		</div>
	</section>
</article>

<style>
	:global(body) {
		background: #f1ede3;
		color: #17191d;
	}

	.progress {
		position: fixed;
		top: 0;
		left: 0;
		right: 0;
		height: 3px;
		z-index: 1000;
		background: transparent;
		pointer-events: none;
	}

	.progress i {
		display: block;
		height: 100%;
		width: 100%;
		transform-origin: left;
		background: linear-gradient(90deg, #5477f5, #ef654d, #e0ad44);
	}

	.story {
		overflow: clip;
	}

	.hero {
		min-height: 100svh;
		position: relative;
		display: grid;
		align-items: center;
		background:
			radial-gradient(circle at 78% 12%, rgb(84 119 245 / 0.25), transparent 30%),
			radial-gradient(circle at 12% 84%, rgb(239 101 77 / 0.19), transparent 28%),
			#10151d;
		color: #f6f0e4;
	}

	.utility {
		position: absolute;
		top: 1.4rem;
		left: max(1.25rem, calc((100vw - 74rem) / 2));
		right: max(1.25rem, calc((100vw - 74rem) / 2));
		display: flex;
		justify-content: space-between;
		align-items: center;
		z-index: 3;
	}

	.utility a {
		color: #d5d9df;
		font-size: 0.85rem;
		text-decoration: none;
	}

	.hero-inner {
		width: min(100% - 2.5rem, 74rem);
		margin-inline: auto;
		padding-block: 15svh 10svh;
	}

	.eyebrow,
	.viz-status,
	.viz-kicker,
	.step-kicker,
	.small-note,
	.source-list span,
	.cost-card small,
	.lab-results small {
		font-family: var(--font-sans, system-ui, sans-serif);
		font-size: 0.72rem;
		font-weight: 750;
		letter-spacing: 0.11em;
		text-transform: uppercase;
	}

	.hero .eyebrow {
		color: #aeb8c7;
	}

	.hero h1 {
		font-family: Georgia, 'Noto Serif SC', serif;
		font-size: clamp(4rem, 10vw, 8.5rem);
		line-height: 0.88;
		letter-spacing: -0.055em;
		margin: 0.18em 0 0.28em;
		max-width: 67rem;
	}

	.hero h1 em {
		color: #ff715b;
		font-style: italic;
	}

	.dek {
		max-width: 48rem;
		font-family: Georgia, 'Noto Serif SC', serif;
		font-size: clamp(1.15rem, 2.1vw, 1.65rem);
		line-height: 1.55;
		color: #d7dce3;
	}

	.hero-meter {
		display: flex;
		align-items: flex-end;
		gap: 1rem;
		margin-top: clamp(2.5rem, 7vh, 5rem);
	}

	.hero-meter strong {
		font-size: clamp(4.5rem, 13vw, 10rem);
		line-height: 0.8;
		letter-spacing: -0.065em;
		font-variant-numeric: tabular-nums;
		color: #ff715b;
	}

	.hero-meter span {
		font-size: 0.85rem;
		color: #aeb8c7;
		padding-bottom: 0.45rem;
	}

	.ticker {
		margin-top: 1.8rem;
		display: inline-flex;
		align-items: center;
		gap: 0.65rem;
		padding: 0.55rem 0.8rem;
		border: 1px solid rgb(255 255 255 / 0.16);
		border-radius: 999px;
		font-size: 0.8rem;
		color: #cdd4df;
		background: rgb(255 255 255 / 0.04);
	}

	.live-dot {
		width: 0.5rem;
		height: 0.5rem;
		border-radius: 50%;
		background: #6ce2b6;
		box-shadow: 0 0 0 0.38rem rgb(108 226 182 / 0.1);
		animation: pulse 2s ease-in-out infinite;
	}

	.scroll-cue {
		margin-top: 3.2rem;
		font-size: 0.72rem;
		letter-spacing: 0.09em;
		color: #8993a1;
	}

	.scrolly-zone {
		padding-block: 10svh 14svh;
		background: #f1ede3;
	}

	.viz-card {
		min-height: min(72svh, 44rem);
		border-radius: 1.7rem;
		padding: clamp(1.4rem, 3.6vw, 3rem);
		box-shadow: 0 2.2rem 6rem rgb(34 30 22 / 0.12);
		display: grid;
		align-content: center;
		background: #fbf8f0;
		border: 1px solid #d9d1c4;
		position: relative;
		overflow: hidden;
	}

	.viz-volume {
		background: linear-gradient(145deg, #edf2ff, #fbf8f0);
	}

	.viz-hidden,
	.viz-contamination {
		background: linear-gradient(145deg, #0e1c29, #143246);
		color: #edf9ff;
		border-color: #28445a;
	}

	.viz-cost,
	.viz-crossing {
		background: linear-gradient(145deg, #191817, #28231d);
		color: #f7ecda;
		border-color: #38332b;
	}

	.viz-status {
		position: absolute;
		top: 1.2rem;
		left: 1.3rem;
		opacity: 0.62;
		margin: 0;
	}

	.viz-kicker {
		opacity: 0.58;
		margin: 0 0 0.75rem;
	}

	.giant-number {
		font-size: clamp(4.3rem, 9.5vw, 8rem);
		font-weight: 850;
		line-height: 0.87;
		letter-spacing: -0.06em;
		font-variant-numeric: tabular-nums;
	}

	.viz-unit {
		margin: 0.55rem 0 1.5rem;
		font-size: 0.85rem;
		opacity: 0.65;
	}

	.metric-row {
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		gap: 0.65rem;
		margin-top: 1.2rem;
	}

	.metric-row > div {
		border: 1px solid rgb(80 78 70 / 0.18);
		border-radius: 0.9rem;
		padding: 0.9rem;
		background: rgb(255 255 255 / 0.35);
	}

	.metric-row strong,
	.metric-row span {
		display: block;
	}

	.metric-row strong {
		font-size: clamp(1.35rem, 2.6vw, 2.2rem);
		line-height: 1;
	}

	.metric-row span {
		font-size: 0.68rem;
		opacity: 0.58;
		margin-top: 0.45rem;
	}

	.small-note {
		margin-top: 1rem;
		line-height: 1.5;
		opacity: 0.58;
		letter-spacing: 0.04em;
		text-transform: none;
	}

	.read-rail {
		height: 3.2rem;
		border-radius: 0.7rem;
		background: #1d2531;
		overflow: hidden;
		margin-top: 1.5rem;
	}

	.read-rail i {
		display: block;
		height: 100%;
		min-width: 3px;
		background: linear-gradient(90deg, #2e9479, #77ccb4);
		transition: width 220ms ease;
	}

	.boundary-grid {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 0.7rem;
	}

	.boundary-card {
		padding: 1rem;
		border: 1px solid #d8d0c1;
		border-radius: 1rem;
		background: #fffdf8;
	}

	.boundary-card small {
		font-size: 0.58rem;
		font-weight: 800;
		color: #766b58;
	}

	.boundary-card strong {
		display: block;
		font-family: Georgia, 'Noto Serif SC', serif;
		font-size: 1.35rem;
		margin-top: 0.35rem;
	}

	.boundary-card p {
		font-size: 0.76rem;
		line-height: 1.55;
		color: #5f594e;
		margin-bottom: 0;
	}

	.iceberg {
		width: min(100%, 30rem);
		height: 23rem;
		margin-inline: auto;
		position: relative;
		display: grid;
		place-items: center;
	}

	.waterline {
		position: absolute;
		left: -30%;
		right: -30%;
		top: 43%;
		height: 1px;
		background: #8dd7e5;
		box-shadow: 0 8rem 0 8rem rgb(17 64 88 / 0.5);
	}

	.ice-tip,
	.ice-under {
		position: absolute;
		left: 50%;
		transform: translateX(-50%);
		text-align: center;
		z-index: 2;
	}

	.ice-tip {
		top: 17%;
		width: 10rem;
		height: 6rem;
		clip-path: polygon(50% 0, 100% 100%, 0 100%);
		background: #d9f3f7;
		color: #173142;
		padding-top: 2.8rem;
	}

	.ice-under {
		top: 43%;
		width: 18rem;
		height: 10.5rem;
		clip-path: polygon(0 0, 100% 0, 68% 100%, 28% 88%);
		background: #75bdd0;
		color: #09283a;
		padding-top: 2.5rem;
	}

	.ice-tip strong,
	.ice-under strong,
	.ice-tip span,
	.ice-under span {
		display: block;
	}

	.ice-tip strong,
	.ice-under strong {
		font-size: 1.4rem;
	}

	.ice-tip span,
	.ice-under span {
		font-size: 0.62rem;
		margin-top: 0.25rem;
	}

	.citation-bar {
		height: 5rem;
		display: flex;
		border-radius: 0.9rem;
		overflow: hidden;
		margin-top: 1.5rem;
		background: #21384a;
	}

	.citation-bar .ack {
		background: #67d2b0;
		min-width: 0.35rem;
	}

	.citation-bar .unack {
		background: #ef6c58;
	}

	.split-labels {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 1rem;
		margin-top: 1rem;
	}

	.split-labels strong,
	.split-labels span {
		display: block;
	}

	.split-labels strong {
		font-size: 2rem;
	}

	.split-labels span {
		font-size: 0.7rem;
		opacity: 0.7;
	}

	.chain {
		display: flex;
		gap: 0.4rem;
		align-items: center;
		flex-wrap: wrap;
		margin-top: 1.4rem;
		font-size: 0.69rem;
		opacity: 0.72;
	}

	.chain span {
		padding: 0.35rem 0.5rem;
		border: 1px solid rgb(255 255 255 / 0.18);
		border-radius: 999px;
	}

	.cost-grid {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 0.8rem;
	}

	.cost-card {
		padding: 1.2rem;
		border: 1px solid rgb(255 255 255 / 0.14);
		border-radius: 1rem;
		background: rgb(255 255 255 / 0.05);
	}

	.cost-card strong,
	.cost-card span {
		display: block;
	}

	.cost-card strong {
		font-size: clamp(2.4rem, 5vw, 4.4rem);
		line-height: 0.95;
		color: #f1c870;
		letter-spacing: -0.045em;
	}

	.cost-card span {
		font-size: 0.72rem;
		opacity: 0.65;
		margin-top: 0.35rem;
	}

	.cost-card p {
		font-size: 0.75rem;
		line-height: 1.5;
		color: #d5cdbd;
	}

	.crossing-years {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 0.75rem;
	}

	.crossing-years > div {
		padding: 1rem;
		border: 1px solid rgb(255 255 255 / 0.14);
		border-radius: 1rem;
		opacity: 0.45;
		transition: opacity 180ms ease, transform 180ms ease;
	}

	.crossing-years > div.active {
		opacity: 1;
		transform: translateY(-0.2rem);
		border-color: #efb953;
	}

	.crossing-years small,
	.crossing-years strong {
		display: block;
	}

	.crossing-years strong {
		font-size: clamp(3.2rem, 7vw, 6rem);
		line-height: 0.95;
		color: #f1c870;
	}

	.timeline {
		position: relative;
		height: 4.5rem;
		margin-top: 2rem;
		border-top: 2px solid #6e6659;
	}

	.timeline i {
		position: absolute;
		top: -0.4rem;
		width: 0.7rem;
		height: 0.7rem;
		border-radius: 50%;
		background: #f1c870;
	}

	.timeline .now { left: 0; }
	.timeline .spike { left: 62%; }
	.timeline .long { left: 100%; transform: translateX(-100%); }
	.timeline span {
		position: absolute;
		top: 0.9rem;
		font-size: 0.68rem;
		color: #cfc7ba;
	}
	.timeline .nlabel { left: 0; }
	.timeline .slabel { left: 62%; transform: translateX(-50%); }
	.timeline .llabel { right: 0; }

	.scenario-result {
		font-size: 0.78rem;
		color: #d8d0c1;
	}

	.step-kicker {
		color: #716859;
		margin: 0 0 0.6rem;
	}

	:global(.scrolly-shell__step-card h2) {
		font-family: Georgia, 'Noto Serif SC', serif;
		letter-spacing: -0.025em;
	}

	.step-note {
		font-size: 0.82rem !important;
		color: #6e675a;
		border-left: 3px solid #d7a54b;
		padding-left: 0.75rem;
	}

	.controls {
		display: grid;
		gap: 1rem;
		margin-top: 1.25rem;
	}

	.controls label,
	.lab-grid label {
		display: grid;
		gap: 0.55rem;
		font-size: 0.78rem;
	}

	input[type='range'] {
		width: 100%;
		min-height: 2.75rem;
		accent-color: #e75e48;
	}

	.scenario-buttons {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 0.55rem;
		margin-top: 1.25rem;
	}

	.scenario-buttons button {
		min-height: 2.8rem;
		border: 1px solid #cfc5b4;
		border-radius: 999px;
		background: #fffaf0;
		color: #302c25;
		font: inherit;
		font-size: 0.72rem;
		cursor: pointer;
	}

	.scenario-buttons button.active {
		background: #24211c;
		color: #fff7e7;
		border-color: #24211c;
	}

	.lab-section {
		background: #fffdf7;
		padding-block: 13svh;
		border-top: 1px solid #ddd4c6;
	}

	.section-inner {
		width: min(100% - 2.5rem, 68rem);
		margin-inline: auto;
	}

	.section-inner.narrow {
		max-width: 52rem;
	}

	.section-inner > h2,
	.closing h2,
	.sources h2 {
		font-family: Georgia, 'Noto Serif SC', serif;
		font-size: clamp(2.4rem, 5.7vw, 5rem);
		line-height: 1.03;
		letter-spacing: -0.045em;
		margin: 0.18em 0 0.4em;
	}

	.section-dek {
		max-width: 48rem;
		font-size: 1.05rem;
		line-height: 1.7;
		color: #625d54;
	}

	.lab-grid {
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		gap: 1rem;
		margin-top: 3rem;
	}

	.lab-grid label {
		padding: 1.1rem;
		border: 1px solid #ded5c6;
		border-radius: 1rem;
		background: #faf5eb;
	}

	.lab-grid b {
		font-size: 1.8rem;
	}

	.lab-results {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 1rem;
		margin-top: 1rem;
	}

	.lab-results article {
		padding: 1.2rem;
		border-radius: 1rem;
		background: #181a1f;
		color: #f7f0e4;
	}

	.lab-results p,
	.lab-results strong,
	.lab-results small {
		display: block;
	}

	.lab-results p {
		font-size: 0.85rem;
		color: #c6c1b7;
	}

	.lab-results strong {
		font-size: clamp(2rem, 4vw, 3.4rem);
		color: #f1c870;
	}

	.lab-results small {
		margin-top: 0.7rem;
		opacity: 0.58;
	}

	.closing {
		background: #12151a;
		color: #f5efe4;
		padding-block: 16svh;
	}

	.closing .eyebrow {
		color: #d3ae69;
	}

	.closing p {
		font-family: Georgia, 'Noto Serif SC', serif;
		font-size: clamp(1.05rem, 2vw, 1.35rem);
		line-height: 1.75;
		color: #c7c3bc;
	}

	.closing-numbers {
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		gap: 0.8rem;
		margin-top: 2.5rem;
	}

	.closing-numbers span {
		border-top: 2px solid #d9ad5e;
		padding-top: 0.8rem;
		font-size: 0.75rem;
		color: #bdb7ac;
	}

	.closing-numbers b {
		display: block;
		font-size: 2.5rem;
		color: #f1c870;
	}

	.sources {
		background: #0c0f13;
		color: #ebe6dc;
		padding-block: 12svh 16svh;
	}

	.sources .section-dek {
		color: #9f9d98;
	}

	.source-list {
		margin-top: 3rem;
		border-top: 1px solid rgb(255 255 255 / 0.13);
	}

	.source-list article {
		display: grid;
		grid-template-columns: 2.4rem 1fr;
		gap: 1rem;
		padding-block: 1rem;
		border-bottom: 1px solid rgb(255 255 255 / 0.1);
	}

	.source-list span {
		color: #8b8e91;
	}

	.source-list a {
		color: #ede8de;
		font-size: 0.9rem;
	}

	.source-list p {
		font-size: 0.76rem;
		line-height: 1.55;
		color: #9c9b97;
		margin: 0.4rem 0 0;
	}

	@keyframes pulse {
		50% { opacity: 0.45; transform: scale(0.72); }
	}

	@media (max-width: 56rem) {
		.hero-inner {
			width: min(100% - 2rem, 42rem);
		}

		.hero h1 {
			font-size: clamp(3.5rem, 16vw, 6rem);
		}

		.metric-row,
		.boundary-grid,
		.cost-grid,
		.crossing-years,
		.lab-grid,
		.lab-results,
		.closing-numbers {
			grid-template-columns: 1fr;
		}

		.viz-card {
			min-height: 44svh;
			border-radius: 0 0 1.25rem 1.25rem;
			padding: 2.5rem 1rem 1rem;
		}

		.giant-number {
			font-size: clamp(3.2rem, 17vw, 6rem);
		}

		.metric-row {
			grid-template-columns: repeat(3, 1fr);
			gap: 0.35rem;
		}

		.metric-row > div {
			padding: 0.55rem;
		}

		.metric-row strong {
			font-size: 1rem;
		}

		.metric-row span {
			font-size: 0.55rem;
		}

		.boundary-grid {
			grid-template-columns: 1fr 1fr;
			gap: 0.35rem;
		}

		.boundary-card {
			padding: 0.65rem;
		}

		.boundary-card strong {
			font-size: 1rem;
		}

		.boundary-card p {
			font-size: 0.62rem;
		}

		.iceberg {
			height: 15rem;
		}

		.ice-tip {
			top: 12%;
			transform: translateX(-50%) scale(0.75);
		}

		.ice-under {
			top: 42%;
			transform: translateX(-50%) scale(0.72);
			transform-origin: top center;
		}

		.citation-bar {
			height: 3.4rem;
		}

		.split-labels strong {
			font-size: 1.4rem;
		}

		.chain {
			display: none;
		}

		.cost-grid,
		.crossing-years {
			grid-template-columns: 1fr 1fr;
		}

		.cost-card {
			padding: 0.75rem;
		}

		.cost-card strong {
			font-size: 1.8rem;
		}

		.cost-card p {
			display: none;
		}

		.crossing-years strong {
			font-size: 2.5rem;
		}

		.section-inner {
			width: min(100% - 2rem, 42rem);
		}

		.scenario-buttons {
			grid-template-columns: 1fr;
		}
	}

	@media (prefers-reduced-motion: reduce) {
		.live-dot {
			animation: none;
		}
		.read-rail i,
		.crossing-years > div {
			transition: none;
		}
	}
</style>
