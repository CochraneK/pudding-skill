<script>
	import { onMount } from 'svelte';
	import facts from '$data/global-mental-health-facts.json';
	import { language } from '$lib/language.js';

	let active = $state(0);
	const byId = Object.fromEntries(facts.facts.map((fact) => [fact.id, fact]));

	const copy = {
		zh: {
			label: '滚动叙事 · 不是仪表盘',
			steps: [
				{
					kicker: '01 · 规模',
					title: '先别急着比较国家。先看问题本身有多大。',
					body: '2021 年，全球约 10.95 亿人生活在精神障碍之中，年龄标化患病率约为 13.6%——接近每 7 人就有 1 人。'
				},
				{
					kicker: '02 · 负担',
					title: '只看死亡，会漏掉精神障碍最主要的健康损失。',
					body: 'GBD 2021 估计精神障碍造成 1.55 亿 DALYs，占全球全部 DALYs 的约 5.4%；其中几乎全部来自带病生存造成的健康损失。'
				},
				{
					kicker: '03 · 钱',
					title: '真正刺眼的差距，出现在系统能够投入多少钱。',
					body: 'WHO Mental Health Atlas 2024 中，报告国家的政府精神健康人均支出中位数，从低收入国家的 0.04 美元到高收入国家的 65.89 美元，相差约 1,647 倍。'
				},
				{
					kicker: '04 · 人',
					title: '钱的差距，最终会变成人力的差距。',
					body: '全球专业精神健康工作人员中位数是每 10 万人 13.5 名；低收入和中低收入环境约为 1.1–2.4，高收入环境则达到 67.2。'
				},
				{
					kicker: '05 · 到达患者',
					title: '系统差距最终落到一个非常具体的问题：能不能得到足够的治疗。',
					body: '一项覆盖 84 个国家的系统综述估计：重度抑郁症患者中，精神健康服务使用率在高收入地区约为 33%，在低/中低收入地区约为 8%；达到最低充分治疗标准的比例约为 23% 对 3%。'
				}
			],
			source: '数据来源：WHO World Mental Health Today 2025、Mental Health Atlas 2024、IHME GBD 2021、PLOS Medicine。'
		},
		en: {
			label: 'SCROLLYTELLING · NOT A DASHBOARD',
			steps: [
				{
					kicker: '01 · SCALE',
					title: 'Before comparing countries, start with the size of the problem.',
					body: 'In 2021, about 1.095 billion people lived with a mental disorder. The age-standardized prevalence was 13.6% — nearly one in seven people worldwide.'
				},
				{
					kicker: '02 · BURDEN',
					title: 'Deaths miss most of the health loss associated with mental disorders.',
					body: 'GBD 2021 attributes 155 million DALYs to mental disorders, about 5.4% of all global DALYs. Almost all of that burden came from years lived with disability.'
				},
				{
					kicker: '03 · MONEY',
					title: 'The sharper divide appears in what systems can afford to spend.',
					body: 'In WHO Mental Health Atlas 2024 reporting countries, median government mental-health spending per person ranges from $0.04 in low-income countries to $65.89 in high-income countries — about a 1,647× gap.'
				},
				{
					kicker: '04 · PEOPLE',
					title: 'The funding gap becomes a workforce gap.',
					body: 'The global median is 13.5 specialized mental-health workers per 100,000 people. Low- and lower-middle-income settings sit around 1.1–2.4; high-income settings reach 67.2.'
				},
				{
					kicker: '05 · REACHING PATIENTS',
					title: 'System capacity ends in a concrete question: does adequate treatment reach people?',
					body: 'A systematic review spanning 84 countries estimated mental-health service use among major-depression cases at 33% in high-income settings versus 8% in low/lower-middle-income settings. Minimally adequate treatment was about 23% versus 3%.'
				}
			],
			source: 'Sources: WHO World Mental Health Today 2025, Mental Health Atlas 2024, IHME GBD 2021, and PLOS Medicine.'
		}
	};

	const t = () => copy[$language];

	onMount(() => {
		const nodes = Array.from(document.querySelectorAll('[data-mental-step]'));
		const observer = new IntersectionObserver(
			(entries) => {
				for (const entry of entries) {
					if (entry.isIntersecting) active = Number(entry.target.dataset.mentalStep || 0);
				}
			},
			{ rootMargin: '-35% 0px -45% 0px', threshold: 0.01 }
		);
		nodes.forEach((node) => observer.observe(node));
		return () => observer.disconnect();
	});
</script>

<section class="scrolly" aria-label={t().label}>
	<div class="graphic-wrap" aria-live="polite">
		<div class="graphic" data-active={active}>
			<div class="graphic-topline">
				<span>{t().label}</span>
				<div class="progress" aria-hidden="true">
					{#each t().steps as _, i}<i class:active={i === active}></i>{/each}
				</div>
			</div>

			<div class="visual-stage">
				<div class="visual prevalence" class:visible={active === 0}>
					<div class="people" aria-hidden="true">
						{#each Array(7) as _, i}<span class:highlight={i === 0}></span>{/each}
					</div>
					<strong>1.095B</strong>
					<p>{byId['global-prevalence-rate-2021'].value} · { $language === 'zh' ? '接近每 7 人 1 人' : 'nearly 1 in 7' }</p>
				</div>

				<div class="visual burden" class:visible={active === 1}>
					<div class="big-pair">
						<div><strong>155M</strong><span>DALYs</span></div>
						<div><strong>5.4%</strong><span>{ $language === 'zh' ? '全球 DALYs' : 'of global DALYs' }</span></div>
					</div>
					<div class="burden-line"><span></span><b></b></div>
					<p>{ $language === 'zh' ? '主要是非致死性健康损失' : 'Mostly nonfatal health loss' }</p>
				</div>

				<div class="visual money" class:visible={active === 2}>
					<div class="money-ends">
						<div><span>{ $language === 'zh' ? '低收入' : 'Low income' }</span><strong>$0.04</strong></div>
						<div class="ratio"><b>1,647×</b><i></i></div>
						<div><span>{ $language === 'zh' ? '高收入' : 'High income' }</span><strong>$65.89</strong></div>
					</div>
					<p>{ $language === 'zh' ? '政府精神健康人均支出中位数' : 'Median government mental-health spending per person' }</p>
				</div>

				<div class="visual workforce" class:visible={active === 3}>
					<div class="work-row"><span>{ $language === 'zh' ? '低 + 中低收入' : 'Low + lower-middle income' }</span><b>1.1–2.4</b><i style="--w: 4%"></i></div>
					<div class="work-row"><span>{ $language === 'zh' ? '全球中位数' : 'Global median' }</span><b>13.5</b><i style="--w: 20%"></i></div>
					<div class="work-row"><span>{ $language === 'zh' ? '高收入' : 'High income' }</span><b>67.2</b><i style="--w: 100%"></i></div>
					<p>{ $language === 'zh' ? '专业精神健康工作人员 / 每 10 万人' : 'specialized mental-health workers / 100k' }</p>
				</div>

				<div class="visual treatment" class:visible={active === 4}>
					<div class="treatment-group">
						<p>{ $language === 'zh' ? '使用精神健康服务' : 'Mental-health service use' }</p>
						<div><span>{ $language === 'zh' ? '高收入' : 'High income' }</span><i style="--w: 82.5%"></i><b>33%</b></div>
						<div><span>{ $language === 'zh' ? '低 + 中低收入' : 'Low + lower-middle' }</span><i style="--w: 20%"></i><b>8%</b></div>
					</div>
					<div class="treatment-group">
						<p>{ $language === 'zh' ? '最低充分治疗' : 'Minimally adequate treatment' }</p>
						<div><span>{ $language === 'zh' ? '高收入' : 'High income' }</span><i style="--w: 57.5%"></i><b>23%</b></div>
						<div><span>{ $language === 'zh' ? '低 + 中低收入' : 'Low + lower-middle' }</span><i style="--w: 7.5%"></i><b>3%</b></div>
					</div>
				</div>
			</div>

			<p class="source-note">{t().source}</p>
	</div>
	</div>

	<div class="steps">
		{#each t().steps as step, i}
			<article class="step" data-mental-step={i} class:active={active === i}>
				<div>
					<p class="step-kicker">{step.kicker}</p>
					<h3>{step.title}</h3>
					<p>{step.body}</p>
				</div>
			</article>
		{/each}
	</div>
</section>

<style>
	.scrolly {
		--ink: #171715;
		--paper: #f5f0e7;
		--panel: #fffaf2;
		--muted: #68645d;
		--accent: #a33f32;
		--line: #d7cfc2;
		position: relative;
		max-width: 1320px;
		margin: 0 auto;
		border-top: 1px solid var(--line);
		border-bottom: 1px solid var(--line);
	}

	.graphic-wrap {
		position: sticky;
		top: 0;
		height: 100vh;
		display: flex;
		align-items: center;
		padding: 4vh clamp(1rem, 4vw, 3rem);
		pointer-events: none;
	}

	.graphic {
		width: min(760px, 58vw);
		min-height: 70vh;
		padding: clamp(1.2rem, 3vw, 2.5rem);
		border: 1px solid var(--line);
		background: rgba(255, 250, 242, 0.96);
		box-shadow: 0 28px 90px rgba(31, 25, 18, 0.09);
		display: flex;
		flex-direction: column;
	}

	.graphic-topline {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 1rem;
		font: 750 0.68rem/1.2 var(--font-mono);
		letter-spacing: 0.09em;
		color: var(--accent);
	}

	.progress { display: flex; gap: 0.28rem; }
	.progress i { width: 18px; height: 3px; background: var(--line); transition: background 260ms ease, width 260ms ease; }
	.progress i.active { width: 34px; background: var(--accent); }

	.visual-stage { position: relative; flex: 1; min-height: 460px; }
	.visual {
		position: absolute;
		inset: 0;
		display: flex;
		flex-direction: column;
		justify-content: center;
		opacity: 0;
		transform: translateY(16px) scale(0.985);
		transition: opacity 360ms ease, transform 520ms cubic-bezier(.2,.75,.2,1);
		pointer-events: none;
	}
	.visual.visible { opacity: 1; transform: none; }
	.visual > p:last-child { margin: 1.2rem 0 0; color: var(--muted); font: 650 0.86rem/1.4 var(--font-sans); }

	.people { display: grid; grid-template-columns: repeat(7, 1fr); gap: clamp(0.35rem, 1vw, 0.7rem); width: min(100%, 560px); margin-bottom: 2.5rem; }
	.people span { aspect-ratio: 1; border-radius: 50%; background: #d7d0c4; transform: scale(0.82); transition: transform 500ms ease, background 500ms ease; }
	.people span.highlight { background: var(--accent); transform: scale(1); }
	.prevalence > strong { font: 800 clamp(5rem, 11vw, 10rem)/0.8 var(--font-sans); letter-spacing: -0.075em; color: var(--accent); }
	.prevalence > p { font-size: 1rem !important; }

	.big-pair { display: grid; grid-template-columns: 1.2fr 0.8fr; gap: 2rem; align-items: end; }
	.big-pair div { border-top: 1px solid var(--line); padding-top: 1.2rem; }
	.big-pair strong { display: block; font: 800 clamp(4.5rem, 9vw, 8rem)/0.85 var(--font-sans); letter-spacing: -0.07em; color: var(--accent); }
	.big-pair span { font: 750 0.9rem/1.2 var(--font-sans); }
	.burden-line { display: flex; margin-top: 2rem; height: 10px; background: #d7d0c4; overflow: hidden; }
	.burden-line span { width: 94.6%; background: var(--accent); }
	.burden-line b { flex: 1; background: #2f3431; }

	.money-ends { display: grid; grid-template-columns: 1fr minmax(110px, 0.55fr) 1fr; align-items: center; gap: 1.2rem; }
	.money-ends > div:not(.ratio) { text-align: center; }
	.money-ends span { display: block; margin-bottom: 0.8rem; font: 750 0.76rem/1.2 var(--font-sans); letter-spacing: 0.06em; text-transform: uppercase; color: var(--muted); }
	.money-ends strong { font: 800 clamp(3.2rem, 6vw, 6rem)/0.9 var(--font-sans); letter-spacing: -0.06em; color: var(--accent); }
	.ratio { text-align: center; }
	.ratio b { display: block; font: 800 clamp(1.6rem, 3vw, 2.8rem)/1 var(--font-sans); }
	.ratio i { display: block; height: 1px; margin-top: 0.9rem; background: var(--ink); position: relative; }
	.ratio i::before, .ratio i::after { content: ''; position: absolute; top: -3px; width: 7px; height: 7px; border-radius: 50%; background: var(--ink); }
	.ratio i::before { left: 0; } .ratio i::after { right: 0; }

	.work-row { display: grid; grid-template-columns: minmax(160px, 1fr) 76px 2fr; gap: 1rem; align-items: center; padding: 0.9rem 0; border-bottom: 1px solid var(--line); }
	.work-row span { color: var(--muted); font: 650 0.82rem/1.25 var(--font-sans); }
	.work-row b { font: 800 1.2rem/1 var(--font-sans); text-align: right; }
	.work-row i { display: block; width: var(--w); height: 18px; background: var(--accent); min-width: 4px; transition: width 700ms cubic-bezier(.2,.75,.2,1); }

	.treatment { gap: 2.2rem; }
	.treatment-group > p { margin: 0 0 0.7rem; font: 750 0.78rem/1.2 var(--font-sans); letter-spacing: 0.06em; text-transform: uppercase; }
	.treatment-group > div { display: grid; grid-template-columns: minmax(145px, 0.8fr) 2fr 50px; gap: 0.8rem; align-items: center; margin: 0.55rem 0; }
	.treatment-group span { font: 600 0.78rem/1.2 var(--font-sans); color: var(--muted); }
	.treatment-group i { display: block; width: var(--w); height: 18px; background: var(--accent); transition: width 700ms cubic-bezier(.2,.75,.2,1); }
	.treatment-group b { font: 800 0.95rem/1 var(--font-sans); }

	.source-note { margin: 0; padding-top: 1rem; border-top: 1px solid var(--line); font: 500 0.68rem/1.4 var(--font-sans); color: var(--muted); }

	.steps {
		position: relative;
		width: min(420px, 34vw);
		margin-left: auto;
		padding: 45vh clamp(1rem, 3vw, 2.5rem) 45vh 0;
		z-index: 2;
	}

	.step { min-height: 74vh; display: flex; align-items: center; }
	.step > div { padding: 1.3rem 1.4rem 1.5rem; border: 1px solid var(--line); background: rgba(245, 240, 231, 0.93); box-shadow: 0 16px 50px rgba(31, 25, 18, 0.07); transition: opacity 250ms ease, transform 250ms ease; opacity: 0.64; }
	.step.active > div { opacity: 1; transform: translateX(-6px); }
	.step-kicker { margin: 0 0 0.7rem; font: 800 0.7rem/1.2 var(--font-mono); letter-spacing: 0.08em; color: var(--accent); }
	.step h3 { margin: 0 0 0.8rem; font: 600 clamp(1.7rem, 2.7vw, 2.7rem)/1.04 var(--font-serif); letter-spacing: -0.035em; }
	.step p:last-child { margin: 0; color: var(--muted); font: 500 0.96rem/1.65 var(--font-sans); }

	@media (max-width: 760px) {
		.graphic-wrap { align-items: flex-start; height: 100svh; padding: 8vh 0.75rem 2vh; }
		.graphic { width: 100%; min-height: 52vh; max-height: 62vh; padding: 1rem; }
		.graphic-topline > span { max-width: 62%; }
		.visual-stage { min-height: 320px; }
		.steps { width: calc(100% - 1.5rem); margin: 0 auto; padding: 55vh 0 30vh; }
		.step { min-height: 72vh; align-items: flex-end; padding-bottom: 8vh; }
		.step > div { width: 100%; background: rgba(245, 240, 231, 0.96); }
		.big-pair { gap: 1rem; }
		.money-ends { grid-template-columns: 1fr; gap: 1rem; }
		.ratio { display: none; }
		.work-row { grid-template-columns: 1fr 58px; }
		.work-row i { grid-column: 1 / -1; width: min(var(--w), 100%); }
		.treatment-group > div { grid-template-columns: minmax(110px, 1fr) 1.5fr 38px; gap: 0.45rem; }
	}

	@media (prefers-reduced-motion: reduce) {
		.visual,
		.progress i,
		.people span,
		.work-row i,
		.treatment-group i,
		.step > div { transition: none; }
	}
</style>
