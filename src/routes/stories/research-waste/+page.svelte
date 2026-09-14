<script>
	import { onMount } from 'svelte';
	import { base } from '$app/paths';
	import facts from '$data/research-waste-facts.json';
	import LanguageToggle from '$components/LanguageToggle.svelte';
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

	const longCross = Math.round(crossingYear(2021, facts.observed_publications['2021'], facts.retraction_anchors['2021'], facts.retraction_growth_cagr_2010_2021));
	const spikeCross = Math.round(crossingYear(2023, observed2023, facts.retraction_anchors['2023_minimum'], facts.retraction_growth_cagr_2010_2023_spike_inclusive));
	const hiddenCriterionPapers = Math.round(observed2023 * facts.estimated_retraction_criterion_share);
	const reviewerFteYears = Math.round(facts.peer_review_hours_2020 / 2000);
	const millionDollarGrants = Math.round(facts.irreproducible_preclinical_cost_usd / 1_000_000);

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

	let perSecond = $derived(modeledAnnual / secondsPerYear);
	let perDay = $derived(modeledAnnual / 365.2425);
	let secondsPerPaper = $derived(1 / perSecond);
	let annualRead = $derived(papersPerDay * 365.2425);
	let annualShare = $derived((annualRead / modeledAnnual) * 100);
	let lifetimeRead = $derived(annualRead * readingYears);
	let lifetimeVsOneYear = $derived((lifetimeRead / modeledAnnual) * 100);
	let worldDuringReadingYears = $derived(modeledAnnual * readingYears);
	let activeCross = $derived(scenario === 'long' ? longCross : spikeCross);
	let activeRetGrowth = $derived(scenario === 'long' ? facts.retraction_growth_cagr_2010_2021 : facts.retraction_growth_cagr_2010_2023_spike_inclusive);
	let paperKg = $derived((facts.retraction_anchors['2023_minimum'] * pagesPerPaper * printCopies * 5) / 1000);
	let deviceKwh = $derived((facts.retraction_anchors['2023_minimum'] * deviceWhPerPaper) / 1000);

	const fmt = (n, digits = 0) => new Intl.NumberFormat($language === 'zh' ? 'zh-CN' : 'en-US', { maximumFractionDigits: digits }).format(n);
	const pct = (n, digits = 2) => `${fmt(n, digits)}%`;

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
		tick();
		const timer = window.setInterval(tick, 1000);
		return () => window.clearInterval(timer);
	});

	const sourceNotesZh = {
		'nsf-publications-2025': 'Scopus 收录的全球科学与工程论文：2010 年约 200 万篇，2021 年 311.7 万篇，2023 年 327.5 万篇。',
		'nature-retractions-2023': '2023 年撤稿数突破 1 万篇；这一异常高峰很大部分来自 Hindawi 集中清理。',
		'nature-retractions-2022': '2010 年约每月 45 篇撤稿，2021 年接近每月 300 篇；作者估计约 1/50 论文可能符合至少一项 COPE 撤稿标准。',
		'retraction-watch-2026': 'Retraction Watch 数据库在 2026 年已超过 6.5 万条撤稿记录。',
		'peer-review-time': '估计 2020 年全球同行评审投入超过 1 亿小时；研究明确说明这很可能仍是低估。',
		'reproducibility-cost': '估计美国临床前生命科学中不可重复研究每年直接关联约 280 亿美元支出；不能外推为所有学科的全球损失。',
		'post-retraction-citations': '13,252 个撤稿后引用语境中，只有 722 个（5.4%）明确提到撤稿。',
		'misconduct-meta-analysis': '2009 年元分析：1.97% 科学家自报曾至少一次伪造、篡改或修改数据/结果；这不是“1.97% 论文造假率”。',
		'paper-mills': 'Nature 引述估计：2000–2022 年至少 40 万篇论文呈现论文工厂特征。',
		'paper-mill-submissions': '一项 2024 年研究引述估计：跨学科约 2% 的期刊投稿来自论文工厂。'
	};

	const copy = {
		zh: {
			back: '← 返回报告库',
			eyebrow: '研究浪费 · 科研诚信 · 论文洪水',
			titleLead: '我们发表得比',
			titleEm: '任何人能读的都快',
			dek: '真正的问题不是“有多少垃圾论文”这么简单，而是：我们每年制造多少知识、多少错误或低价值研究漏过筛选、多少时间和资金被它们吸走，以及错误在撤稿之后还会传播多久。',
			baseline: '可核验基线',
			baselineTitle: '2023 年，Scopus 收录的全球科学与工程论文约 327.5 万篇。',
			modelNote: '下面的“今天 / 今年 / 打开页面以来”不是实时数据库查询，而是把 2010–2023 年的历史增长率继续到当前年份后的节奏模型。',
			today: '模型估计：今天已经发表',
			year: '模型估计：今年打开页面前已经发表',
			since: '从你打开这个页面以来',
			papers: '篇',
			perYear: '篇 / 年（当前趋势模型）',
			perDay: '篇 / 天',
			perSecond: '篇 / 秒',
			every: '平均每',
			seconds: '秒一篇',
			readEyebrow: '个人阅读能力 vs. 论文生产线',
			readTitle: '一天读 N 篇，一辈子仍然只碰到知识海洋的一小层。',
			readPerDay: '每天完整读',
			readYears: '持续阅读年数',
			annualShare: '你每年能读完当年论文的',
			lifetime: '这段“学术阅读生涯”共读',
			lifetimeOneYear: '只相当于当前一年产量的',
			worldProduces: '如果产量不再增长，同期世界仍会新增约',
			boundaryEyebrow: '先把概念分开',
			boundaryTitle: '“无用学术”不是一个可以直接统计的变量。',
			boundaryDek: '撤稿、造假、不可重复、论文工厂、低价值研究彼此重叠，但不是同义词。把它们混成一个百分比，本身就是坏统计。',
			boundaries: [
				['已撤稿', '已经被期刊正式撤回的可观察子集；撤稿也可能源于诚实错误，并不等于造假。'],
				['应撤未撤', 'Retraction Watch 创办者曾估计约 1/50 论文可能符合至少一项 COPE 撤稿标准；这是粗略风险估计，不是已证实造假。'],
				['不可重复', '结果无法被可靠重现，原因可能是设计、材料、统计、报告或环境差异；同样不等于故意不端。'],
				['低价值 / 无效问题', '研究问题不重要、设计无法回答问题、结果无法影响决策等。它高度依赖领域和目的，不存在可信的全球统一“无用率”。']
			],
			hiddenEyebrow: '被发现的只是表层',
			hiddenTitle: '如果“1/50 可能达到撤稿标准”的估计只是数量级正确，一年就是约 6.55 万篇。',
			hiddenDek: '把 2% 机械套到 2023 年 327.5 万篇产量，得到约 65,500 篇“可能达到至少一项撤稿标准”的论文。这个数字不能和 2023 年 1 万篇撤稿直接相减，因为撤稿发生在不同发表年份，而且 2023 年本身是一次异常集中清理。',
			retracted2023: '2023 年撤稿 >10,000',
			dbTotal: '2026 年数据库累计 >65,000',
			paperMill: '2000–2022 年约 400,000 篇呈论文工厂特征（估计）',
			contamEyebrow: '错误不会在撤稿按钮处停止',
			contamTitle: '撤稿后，论文仍然会进入后续研究的参考文献。',
			contamDek: '一项数据库级生物医学研究分析了 13,252 个撤稿后引用语境，只有 5.4% 明确提到被引论文已经撤稿。剩余引用并不都等于“误用”，但它说明撤稿标签没有自动切断知识传播。',
			ack: '明确承认撤稿',
			noAck: '没有明确承认撤稿',
			downstream: ['论文', '综述 / Meta', '学生论文', '新实验', '基金申请', '政策 / 临床线索'],
			costEyebrow: '真正昂贵的不是 PDF',
			costTitle: '时间与研发资源的机会成本，远大于纸张本身。',
			peerTitle: '同行评审劳动',
			peerBody: '2020 年全球同行评审被估计投入超过 1 亿小时。按每个全职研究年 2,000 小时换算，约等于 5 万个 FTE 年。这里不是说这些时间“全浪费”，而是显示发表系统本身吞吐了多少人类注意力。',
			moneyTitle: '不可重复的临床前研究',
			moneyBody: '2015 年研究估计，美国临床前生命科学每年约 280 亿美元花在不可重复研究上。它是特定领域、特定年代的估计，不应冒充“全球学术浪费总额”。',
			opportunity: '容量等价，而不是价值预测',
			opportunityBody: '280 亿美元相当于 28,000 个每项 100 万美元的研究项目；1 亿小时相当于约 50,000 个 2,000 小时的研究年。我们可以比较“还能做多少事”，但不能声称这些资源一定会创造某个固定社会回报。',
			materialEyebrow: '纸张、电费：只做透明情景，不伪装成测量',
			materialTitle: '如果你一定要算物理资源，先把假设摆在桌面上。',
			pages: '每篇打印页数',
			copies: '每篇打印份数',
			device: '每篇数字阅读耗电（Wh）',
			paperResult: '按 10,000 篇撤稿论文计算，纸张约',
			energyResult: '数字阅读耗电约',
			materialNote: '默认按 A4 80gsm 约 5g/张估算。这里只算最终论文的一次打印/阅读，不包括实验设备、服务器、训练、差旅、草稿和重复实验，因此绝不能把这个数叫作“总环境成本”。',
			crossEyebrow: '“撤稿什么时候跑赢发表？”',
			crossTitle: '答案可以差 17 年——只因为你选了不同的增长窗口。',
			crossDek: '这是故意做的反误导演示：交叉点是指数外推的数学结果，不是对未来学术系统的预测。撤稿增长也可能意味着筛查能力变强，而不只是造假变多。',
			long: '长期、避开 2023 清理峰值',
			spike: '把 2023 清理峰值也当长期趋势',
			retGrowth: '撤稿年增长假设',
			pubGrowth: '论文年增长基线',
			crossAt: '机械交叉点',
			crossWarning: '如果看到有人只展示“2054 年撤稿超过发表”而不展示窗口选择，这个数字本身就是需要审稿的。',
			endingEyebrow: '真正的危机不是某一天曲线相交',
			endingTitle: '危机是筛选、纠错与阅读能力，长期追不上生产速度。',
			endingDek: '科学不需要停止发表，而需要让“值得做的问题、透明的方法、可复核的证据、及时的纠错”获得比单纯论文数量更高的奖励。否则我们制造的不是知识库，而是越来越昂贵的搜索问题。',
			sources: '来源与计算边界',
			sourcesTitle: '所有冲击性数字，都把“观察值 / 估计 / 情景”分开。'
		},
		en: {
			back: '← Back to report library',
			eyebrow: 'RESEARCH WASTE · INTEGRITY · PAPER FLOOD',
			titleLead: 'We publish faster than',
			titleEm: 'anyone can read',
			dek: 'The real question is not simply “how much research is junk?” It is how much knowledge we produce, how much error or low-value work survives filtering, how much time and money it absorbs, and how long flawed work keeps propagating after correction.',
			baseline: 'AUDITED BASELINE', baselineTitle: 'In 2023, Scopus indexed about 3.275 million science and engineering articles worldwide.',
			modelNote: 'The “today / this year / since open” counters are not live publication-database queries. They extend the observed 2010–2023 growth rate into the current year as a pace model.',
			today: 'Modeled papers published today', year: 'Modeled papers published this year before you opened the page', since: 'Since you opened this page', papers: 'papers',
			perYear: 'papers / year (current trend model)', perDay: 'papers / day', perSecond: 'papers / second', every: 'about one every', seconds: 'seconds',
			readEyebrow: 'ONE READER VS. THE PAPER MACHINE', readTitle: 'Read N papers a day and a lifetime still touches only a thin layer of the literature.', readPerDay: 'Full papers per day', readYears: 'Years at that pace', annualShare: 'Share of one year you can read', lifetime: 'Papers across that reading life', lifetimeOneYear: 'Equivalent to this share of just one current year', worldProduces: 'Even with zero future growth, the world would add about',
			boundaryEyebrow: 'SEPARATE THE CATEGORIES FIRST', boundaryTitle: '“Useless research” is not one measurable variable.', boundaryDek: 'Retraction, fraud, irreproducibility, paper mills, and low-value research overlap but are not synonyms. Collapsing them into one percentage would itself be bad measurement.',
			boundaries: [['Retracted', 'The observable set formally withdrawn by journals. Retractions can also result from honest error; retraction is not synonymous with fraud.'], ['Retraction-worthy but undiscovered', 'Retraction Watch’s co-founder has estimated roughly 1 in 50 papers could meet at least one COPE retraction criterion. This is a rough risk estimate, not proven fraud.'], ['Irreproducible', 'Results cannot be reliably reproduced for reasons that may include design, materials, statistics, reporting, or context. Again, not equivalent to intent.'], ['Low-value / low-utility', 'Questions that do not matter, designs that cannot answer them, or findings unlikely to change decisions. This is purpose- and field-dependent; there is no credible global “uselessness rate.”']],
			hiddenEyebrow: 'WHAT WE SEE IS THE SURFACE', hiddenTitle: 'If the “1 in 50 may meet retraction criteria” estimate is even order-of-magnitude right, one year implies roughly 65,500 papers.', hiddenDek: 'Applying 2% mechanically to the 3.275M papers in 2023 gives about 65,500 potentially retraction-criterion papers. You cannot subtract the 10,000 retractions issued in 2023 from that number: retractions span publication cohorts, and 2023 was itself an exceptional cleanup year.', retracted2023: '2023 retractions >10,000', dbTotal: 'Database total in 2026 >65,000', paperMill: '≈400,000 papers with paper-mill hallmarks, 2000–2022 (estimate)',
			contamEyebrow: 'ERROR DOES NOT STOP AT THE RETRACTION BUTTON', contamTitle: 'Retracted papers still enter the reference lists of later research.', contamDek: 'A database-wide biomedical study examined 13,252 post-retraction citation contexts. Only 5.4% explicitly acknowledged that the cited paper had been retracted. Not every unacknowledged citation is misuse, but the result shows that a retraction label does not automatically stop knowledge propagation.', ack: 'Acknowledged retraction', noAck: 'Did not explicitly acknowledge', downstream: ['Paper', 'Review / meta-analysis', 'Student thesis', 'New experiment', 'Grant proposal', 'Policy / clinical lead'],
			costEyebrow: 'THE EXPENSIVE PART IS NOT THE PDF', costTitle: 'Human attention and R&D opportunity costs dominate the story.', peerTitle: 'Peer-review labor', peerBody: 'Global peer review was estimated at more than 100 million hours in 2020. At 2,000 hours per full-time research year, that is roughly 50,000 FTE-years. This does not mean all review time is wasted; it shows the scale of attention consumed by the publication system.', moneyTitle: 'Irreproducible preclinical research', moneyBody: 'A 2015 study estimated roughly $28B per year in US preclinical life-science spending associated with irreproducible research. It is a field- and era-specific estimate, not a global academic-waste total.', opportunity: 'Capacity equivalence, not a value forecast', opportunityBody: '$28B is the same budget capacity as 28,000 $1M research projects; 100M hours is about 50,000 2,000-hour research years. We can compare what else could fit into that capacity, but not claim a fixed social return.',
			materialEyebrow: 'PAPER + ELECTRICITY: TRANSPARENT SCENARIO ONLY', materialTitle: 'If you want a physical-resource number, expose the assumptions first.', pages: 'Printed pages per paper', copies: 'Printed copies per paper', device: 'Digital reading electricity per paper (Wh)', paperResult: 'For 10,000 retracted papers, modeled paper mass is', energyResult: 'Modeled digital-reading electricity is', materialNote: 'Default paper mass assumes roughly 5g per A4 80gsm sheet. This covers one final-paper print/read scenario only—no lab equipment, servers, training, travel, drafts, or replication—so it must not be called total environmental cost.',
			crossEyebrow: '“WHEN DO RETRACTIONS OVERTAKE PUBLICATIONS?”', crossTitle: 'The answer moves by 17 years just by changing the growth window.', crossDek: 'This is deliberately an anti-misleading demonstration: the crossover is an exponential extrapolation, not a forecast. Retraction growth can also signal stronger detection rather than more misconduct.', long: 'Long-run, excluding the 2023 cleanup spike', spike: 'Treat the 2023 cleanup spike as persistent', retGrowth: 'Retraction growth assumption', pubGrowth: 'Publication growth baseline', crossAt: 'Mechanical crossover', crossWarning: 'If someone shows “retractions overtake publications in 2054” without showing the window choice, that number itself needs peer review.',
			endingEyebrow: 'THE CRISIS IS NOT A SINGLE CROSSING DATE', endingTitle: 'The crisis is correction, filtering, and human reading capacity falling behind production.', endingDek: 'Science does not need to stop publishing. It needs stronger rewards for worthwhile questions, transparent methods, checkable evidence, and fast correction than for paper count alone. Otherwise the knowledge base becomes an increasingly expensive search problem.', sources: 'SOURCES + COMPUTATION BOUNDARIES', sourcesTitle: 'Every dramatic number is labeled as observation, estimate, or scenario.'
		}
	};
	const t = () => copy[$language];
</script>

<svelte:head>
	<title>{t().titleLead} {t().titleEm} · pudding-skill</title>
	<meta name="description" content={t().dek} />
	<meta property="og:title" content={`${t().titleLead} ${t().titleEm}`} />
	<meta property="og:description" content={t().dek} />
	<meta name="theme-color" content="#f1eee7" />
	<link rel="canonical" href="https://cochranek.github.io/pudding-skill/stories/research-waste/" />
</svelte:head>

<article class="story" data-story-kind="research-waste" data-publication-baseline="3275079">
	<section class="hero">
		<div class="utility"><a href={`${base}/`}>{t().back}</a><LanguageToggle /></div>
		<p class="kicker">{t().eyebrow}</p>
		<h1>{t().titleLead}<br /><em>{t().titleEm}</em></h1>
		<p class="dek">{t().dek}</p>
	</section>

	<section class="pace section-dark">
		<div class="section-head"><p class="eyebrow">{t().baseline}</p><h2>{t().baselineTitle}</h2><p>{t().modelNote}</p></div>
		<div class="pace-grid">
			<div class="big-stat"><strong>{fmt(modeledAnnual)}</strong><span>{t().perYear}</span></div>
			<div><strong>{fmt(perDay)}</strong><span>{t().perDay}</span></div>
			<div><strong>{fmt(perSecond, 3)}</strong><span>{t().perSecond}</span></div>
			<div><strong>{fmt(secondsPerPaper, 1)}</strong><span>{t().every} {t().seconds}</span></div>
		</div>
		<div class="live-grid" aria-live="polite">
			<div><span>{t().today}</span><strong>{fmt(todayCount)}</strong><small>{t().papers}</small></div>
			<div><span>{t().year}</span><strong>{fmt(yearCountAtOpen)}</strong><small>{t().papers}</small></div>
			<div><span>{t().since}</span><strong>{fmt(sinceOpen, 1)}</strong><small>{t().papers}</small></div>
		</div>
	</section>

	<section class="reading section-light">
		<div class="section-head"><p class="eyebrow">{t().readEyebrow}</p><h2>{t().readTitle}</h2></div>
		<div class="calculator">
			<label><span>{t().readPerDay}: <b>{papersPerDay}</b></span><input type="range" min="1" max="50" step="1" bind:value={papersPerDay} /></label>
			<label><span>{t().readYears}: <b>{readingYears}</b></span><input type="range" min="10" max="70" step="5" bind:value={readingYears} /></label>
		</div>
		<div class="read-results">
			<div><span>{t().annualShare}</span><strong>{pct(annualShare, 3)}</strong></div>
			<div><span>{t().lifetime}</span><strong>{fmt(lifetimeRead)}</strong></div>
			<div><span>{t().lifetimeOneYear}</span><strong>{pct(lifetimeVsOneYear, 2)}</strong></div>
			<div><span>{t().worldProduces}</span><strong>{fmt(worldDuringReadingYears)}</strong></div>
		</div>
	</section>

	<section class="boundaries section-paper">
		<div class="section-head"><p class="eyebrow">{t().boundaryEyebrow}</p><h2>{t().boundaryTitle}</h2><p>{t().boundaryDek}</p></div>
		<div class="boundary-grid">{#each t().boundaries as item, i}<article><span>0{i + 1}</span><h3>{item[0]}</h3><p>{item[1]}</p></article>{/each}</div>
	</section>

	<section class="hidden section-red">
		<div class="section-head"><p class="eyebrow">{t().hiddenEyebrow}</p><h2>{t().hiddenTitle}</h2><p>{t().hiddenDek}</p></div>
		<div class="hidden-number"><strong>{fmt(hiddenCriterionPapers)}</strong><span>≈ 2% × 3,275,079</span></div>
		<div class="evidence-strip"><div>{t().retracted2023}</div><div>{t().dbTotal}</div><div>{t().paperMill}</div></div>
	</section>

	<section class="contamination section-light">
		<div class="section-head"><p class="eyebrow">{t().contamEyebrow}</p><h2>{t().contamTitle}</h2><p>{t().contamDek}</p></div>
		<div class="citation-meter" role="img" aria-label="5.4 percent of post-retraction citation contexts acknowledged the retraction">
			<div class="ack" style={`width:${facts.post_retraction_acknowledgement_share * 100}%`}></div><div class="rest"></div>
		</div>
		<div class="meter-labels"><span><b>5.4%</b> {t().ack}</span><span><b>94.6%</b> {t().noAck}</span></div>
		<div class="downstream">{#each t().downstream as node, i}<div><span>{String(i + 1).padStart(2, '0')}</span>{node}</div>{/each}</div>
	</section>

	<section class="cost section-dark">
		<div class="section-head"><p class="eyebrow">{t().costEyebrow}</p><h2>{t().costTitle}</h2></div>
		<div class="cost-grid">
			<article><strong>100M+</strong><h3>{t().peerTitle}</h3><p>{t().peerBody}</p><small>≈ {fmt(reviewerFteYears)} FTE-years</small></article>
			<article><strong>$28B</strong><h3>{t().moneyTitle}</h3><p>{t().moneyBody}</p><small>≈ {fmt(millionDollarGrants)} × $1M</small></article>
		</div>
		<div class="opportunity"><p class="eyebrow">{t().opportunity}</p><p>{t().opportunityBody}</p></div>
	</section>

	<section class="materials section-paper">
		<div class="section-head"><p class="eyebrow">{t().materialEyebrow}</p><h2>{t().materialTitle}</h2></div>
		<div class="material-controls">
			<label>{t().pages}<input type="number" min="1" max="100" bind:value={pagesPerPaper} /></label>
			<label>{t().copies}<input type="number" min="0" max="20" bind:value={printCopies} /></label>
			<label>{t().device}<input type="number" min="0" max="2000" step="10" bind:value={deviceWhPerPaper} /></label>
		</div>
		<div class="material-results"><div><span>{t().paperResult}</span><strong>{fmt(paperKg, 1)} kg</strong></div><div><span>{t().energyResult}</span><strong>{fmt(deviceKwh, 1)} kWh</strong></div></div>
		<p class="caveat">{t().materialNote}</p>
	</section>

	<section class="cross section-light">
		<div class="section-head"><p class="eyebrow">{t().crossEyebrow}</p><h2>{t().crossTitle}</h2><p>{t().crossDek}</p></div>
		<div class="scenario-buttons" role="group" aria-label="Retraction growth scenario">
			<button class:active={scenario === 'long'} onclick={() => scenario = 'long'}>{t().long}</button>
			<button class:active={scenario === 'spike'} onclick={() => scenario = 'spike'}>{t().spike}</button>
		</div>
		<div class="cross-result">
			<div><span>{t().retGrowth}</span><strong>{pct(activeRetGrowth * 100, 1)}</strong></div>
			<div><span>{t().pubGrowth}</span><strong>{pct(pubGrowth * 100, 1)}</strong></div>
			<div class="year"><span>{t().crossAt}</span><strong>{activeCross}</strong></div>
		</div>
		<div class="timeline"><span>2023</span><i style={`width:${Math.min(100, ((activeCross - 2023) / 55) * 100)}%`}></i><span>{activeCross}</span></div>
		<p class="warning">{t().crossWarning}</p>
	</section>

	<section class="ending section-red"><p class="eyebrow">{t().endingEyebrow}</p><h2>{t().endingTitle}</h2><p>{t().endingDek}</p></section>

	<section class="sources section-paper">
		<div class="section-head"><p class="eyebrow">{t().sources}</p><h2>{t().sourcesTitle}</h2></div>
		<div class="source-list">{#each facts.sources as source, i}<article><span>{String(i + 1).padStart(2, '0')}</span><div><a href={source.url} target="_blank" rel="noreferrer">{source.label} ↗</a><p>{$language === 'zh' ? sourceNotesZh[source.id] : source.note}</p></div></article>{/each}</div>
	</section>
</article>

<style>
	:global(body){background:#f1eee7;color:#171715}.story{--paper:#f1eee7;--ink:#171715;--muted:#68635d;--red:#a4312f;--line:#cec7bc;--cream:#fffaf1;min-height:100vh}.hero,.section-light,.section-paper,.section-dark,.section-red{padding-left:max(24px,calc((100vw - 1180px)/2));padding-right:max(24px,calc((100vw - 1180px)/2))}.hero{padding-top:3rem;padding-bottom:8rem}.utility{display:flex;justify-content:space-between;align-items:center;gap:1rem;margin-bottom:clamp(5rem,10vw,9rem);font:700 .78rem/1.2 var(--font-mono)}.utility a{color:inherit}.kicker,.eyebrow{font:750 .72rem/1.3 var(--font-mono);letter-spacing:.11em;text-transform:uppercase;color:var(--red)}h1,h2,h3{font-family:var(--font-serif)}h1{max-width:1100px;margin:.2em 0 .3em;font-size:clamp(4rem,10vw,9rem);line-height:.86;letter-spacing:-.065em}h1 em{color:var(--red);font-weight:400}.dek{max-width:820px;font-size:clamp(1.15rem,2vw,1.5rem);line-height:1.6;color:var(--muted)}.section-head{display:grid;grid-template-columns:1fr 1fr;gap:1.5rem 4rem;align-items:end;max-width:1180px;margin:0 auto 3rem}.section-head .eyebrow{grid-column:1/-1}.section-head h2{margin:0;font-size:clamp(2.8rem,6vw,5.8rem);line-height:.94;letter-spacing:-.05em}.section-head>p:last-child:not(.eyebrow){margin:0;max-width:58ch;line-height:1.65;color:inherit;opacity:.72}.section-dark{background:#171715;color:#f6f1e8;padding-top:7rem;padding-bottom:7rem}.section-dark .eyebrow{color:#f08f7f}.section-red{background:var(--red);color:#fff7ed;padding-top:7rem;padding-bottom:7rem}.section-red .eyebrow{color:#ffd1c9}.section-light{background:var(--cream);padding-top:7rem;padding-bottom:7rem}.section-paper{background:var(--paper);padding-top:7rem;padding-bottom:7rem}.pace-grid{display:grid;grid-template-columns:2fr repeat(3,1fr);max-width:1180px;margin:0 auto;border-top:1px solid #4b4944;border-bottom:1px solid #4b4944}.pace-grid>div{padding:1.5rem;border-right:1px solid #4b4944}.pace-grid>div:last-child{border-right:0}.pace-grid strong,.pace-grid span{display:block}.pace-grid strong{font:800 clamp(2.5rem,5vw,5rem)/.95 var(--font-sans);letter-spacing:-.055em}.pace-grid span{margin-top:.8rem;color:#bbb5ab;font-size:.82rem}.live-grid{display:grid;grid-template-columns:repeat(3,1fr);max-width:1180px;margin:3rem auto 0;gap:1rem}.live-grid>div{padding:1.4rem;border:1px solid #4b4944}.live-grid span,.live-grid small,.live-grid strong{display:block}.live-grid span{min-height:2.8em;color:#bbb5ab}.live-grid strong{margin:.7rem 0;font:750 clamp(2rem,4vw,4rem)/1 var(--font-mono);color:#fff}.live-grid small{color:#8d8981}.calculator,.read-results,.boundary-grid,.evidence-strip,.cost-grid,.material-controls,.material-results,.cross-result,.source-list,.downstream{max-width:1180px;margin-left:auto;margin-right:auto}.calculator{display:grid;grid-template-columns:1fr 1fr;gap:2rem;padding:2rem;background:#171715;color:#fff}.calculator label{display:grid;gap:1rem}.calculator input{width:100%}.read-results{display:grid;grid-template-columns:repeat(4,1fr);border:1px solid var(--line);border-top:0}.read-results>div{padding:1.5rem;border-right:1px solid var(--line)}.read-results>div:last-child{border-right:0}.read-results span,.read-results strong{display:block}.read-results span{min-height:3.4em;color:var(--muted);line-height:1.35}.read-results strong{margin-top:1rem;font:800 clamp(2rem,4vw,4rem)/1 var(--font-sans);letter-spacing:-.04em;color:var(--red)}.boundary-grid{display:grid;grid-template-columns:repeat(4,1fr);border-top:1px solid var(--line)}.boundary-grid article{padding:1.5rem;border-right:1px solid var(--line);border-bottom:1px solid var(--line)}.boundary-grid article:last-child{border-right:0}.boundary-grid article>span{font:700 .75rem var(--font-mono);color:var(--red)}.boundary-grid h3{font-size:1.7rem;margin:.8rem 0}.boundary-grid p{color:var(--muted);line-height:1.6}.hidden-number{max-width:1180px;margin:4rem auto}.hidden-number strong{display:block;font:900 clamp(5rem,16vw,13rem)/.75 var(--font-sans);letter-spacing:-.08em}.hidden-number span{display:block;margin-top:2rem;font-family:var(--font-mono)}.evidence-strip{display:grid;grid-template-columns:repeat(3,1fr);border-top:1px solid #d5685c;border-bottom:1px solid #d5685c}.evidence-strip div{padding:1.5rem;border-right:1px solid #d5685c}.evidence-strip div:last-child{border-right:0}.citation-meter{display:flex;max-width:1180px;height:72px;margin:0 auto;background:#d7d0c5}.citation-meter .ack{background:var(--red)}.citation-meter .rest{flex:1;background:#cfc8bd}.meter-labels{display:flex;justify-content:space-between;max-width:1180px;margin:1rem auto 4rem;color:var(--muted)}.meter-labels b{color:var(--ink)}.downstream{display:grid;grid-template-columns:repeat(6,1fr);border-top:1px solid var(--line);border-bottom:1px solid var(--line)}.downstream div{position:relative;padding:1.5rem .8rem;min-height:100px;border-right:1px solid var(--line);font:650 .9rem/1.35 var(--font-sans)}.downstream div::after{content:'→';position:absolute;right:-8px;top:45%;z-index:2;background:var(--cream);padding:0 2px;color:var(--red)}.downstream div:last-child{border-right:0}.downstream div:last-child::after{display:none}.downstream span{display:block;margin-bottom:.8rem;color:var(--red);font-family:var(--font-mono)}.cost-grid{display:grid;grid-template-columns:1fr 1fr;gap:1px;background:#4b4944}.cost-grid article{background:#171715;padding:2rem}.cost-grid article>strong{font:900 clamp(4rem,9vw,8rem)/.9 var(--font-sans);letter-spacing:-.07em;color:#f08f7f}.cost-grid h3{font-size:2rem;margin:1rem 0}.cost-grid p{color:#c6c0b6;line-height:1.65}.cost-grid small{font:700 .8rem var(--font-mono);color:#f08f7f}.opportunity{max-width:1180px;margin:3rem auto 0;padding-top:2rem;border-top:1px solid #4b4944}.opportunity p:last-child{max-width:80ch;color:#c6c0b6;line-height:1.65}.material-controls{display:grid;grid-template-columns:repeat(3,1fr);gap:1rem}.material-controls label{display:grid;gap:.6rem;font:700 .78rem var(--font-mono);text-transform:uppercase;letter-spacing:.05em}.material-controls input{min-height:48px;padding:0 .8rem;border:1px solid var(--line);background:#fff;color:var(--ink);font:700 1rem var(--font-mono)}.material-results{display:grid;grid-template-columns:1fr 1fr;margin-top:1rem;border:1px solid var(--line)}.material-results>div{padding:2rem}.material-results>div+div{border-left:1px solid var(--line)}.material-results span,.material-results strong{display:block}.material-results span{color:var(--muted)}.material-results strong{margin-top:1rem;font:850 clamp(3rem,6vw,6rem)/1 var(--font-sans);color:var(--red)}.caveat{max-width:1180px;margin:1.5rem auto 0;color:var(--muted);font-size:.86rem;line-height:1.6}.scenario-buttons{display:flex;max-width:1180px;margin:0 auto 1rem;gap:.6rem;flex-wrap:wrap}.scenario-buttons button{min-height:44px;padding:.75rem 1rem;border:1px solid var(--ink);background:transparent;color:var(--ink);font-weight:750}.scenario-buttons button.active{background:var(--ink);color:#fff}.cross-result{display:grid;grid-template-columns:1fr 1fr 1.2fr;border:1px solid var(--line)}.cross-result>div{padding:1.5rem;border-right:1px solid var(--line)}.cross-result>div:last-child{border-right:0}.cross-result span,.cross-result strong{display:block}.cross-result span{color:var(--muted)}.cross-result strong{margin-top:.7rem;font:800 clamp(2.5rem,5vw,5rem)/1 var(--font-sans)}.cross-result .year strong{color:var(--red)}.timeline{display:flex;align-items:center;max-width:1180px;margin:2rem auto 0;gap:1rem;font:700 .8rem var(--font-mono)}.timeline i{display:block;height:12px;background:var(--red);min-width:8%}.warning{max-width:1180px;margin:2rem auto 0;padding:1rem 1.2rem;border-left:5px solid var(--red);background:#f1e5e2;font-weight:650;line-height:1.55}.ending h2{max-width:1080px;margin:.25em 0;font-size:clamp(3.5rem,8vw,7.5rem);line-height:.9;letter-spacing:-.06em}.ending>p:last-child{max-width:800px;font-size:1.2rem;line-height:1.65}.source-list{border-top:1px solid var(--line)}.source-list article{display:grid;grid-template-columns:60px 1fr;gap:1rem;padding:1.25rem 0;border-bottom:1px solid var(--line)}.source-list article>span{font:700 .8rem var(--font-mono);color:var(--red)}.source-list a{font-weight:750;color:var(--ink)}.source-list p{max-width:90ch;margin:.5rem 0 0;color:var(--muted);line-height:1.55}
	@media(max-width:800px){.section-head{grid-template-columns:1fr}.pace-grid{grid-template-columns:1fr 1fr}.pace-grid>div{border-bottom:1px solid #4b4944}.live-grid,.read-results,.boundary-grid,.evidence-strip,.cost-grid,.material-controls,.material-results,.cross-result{grid-template-columns:1fr}.live-grid{gap:.6rem}.read-results>div,.boundary-grid article,.evidence-strip div,.cross-result>div{border-right:0;border-bottom:1px solid var(--line)}.cost-grid{gap:1px}.calculator{grid-template-columns:1fr}.downstream{grid-template-columns:1fr 1fr}.downstream div:nth-child(2n){border-right:0}.downstream div::after{display:none}.material-results>div+div{border-left:0;border-top:1px solid var(--line)}.meter-labels{flex-direction:column;gap:.4rem}.hidden-number strong{font-size:clamp(4rem,24vw,8rem)}}
</style>
