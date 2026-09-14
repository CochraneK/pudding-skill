<script>
	import Meta from "$components/Meta.svelte";
	import candidates from "$data/story-candidates.json";
	import selection from "$data/story-selection.json";
	import evaluation from "$data/story-evaluation.json";
	import claimAudit from "$data/story-claim-audit.json";

	const components = [
		["evidence", "Evidence"],
		["coverage", "Coverage"],
		["effect", "Effect"],
		["distinctiveness", "Distinctiveness"],
		["visual_fit", "Visual fit"],
		["question_relevance", "Question match"]
	];

	function pct(value) {
		return `${Math.max(0, Math.min(100, Number(value || 0)))}%`;
	}
</script>

<Meta title="Editorial Lab · pudding-skill" description="Inspect ranked story candidates and deterministic editorial scoring." />

<svelte:head>
	<meta name="robots" content="noindex" />
</svelte:head>

<section class="lab-shell">
	<header class="hero">
		<p class="eyebrow">EDITORIAL LAB · V2.2</p>
		<h1>Don’t generate the first story. <em>Compare the plausible ones.</em></h1>
		<p class="dek">
			The pipeline found {candidates.candidate_count} evidence-backed directions in <strong>{candidates.source_file}</strong>, scored them with transparent proxies, then selected the first candidate that passed structural, editorial, and renderer gates.
		</p>
		<div class="status-row">
			<span class:pass={selection.status === "PASS"}>{selection.status}</span>
			<span>selected rank #{selection.selected_rank}</span>
			<span>score {selection.selected_score}</span>
			<span>{selection.attempt_count} selection attempt{selection.attempt_count === 1 ? "" : "s"}</span>
		</div>
	</header>

	<section class="selected-panel">
		<div>
			<p class="section-label">Selected direction</p>
			<h2>{candidates.candidates.find((d) => d.id === selection.selected_candidate_id)?.claim}</h2>
			<p class="note">{selection.note}</p>
		</div>
		<a href="/generated">Open generated story →</a>
	</section>

	<section class="board">
		<div class="board-head">
			<div>
				<p class="section-label">Candidate board</p>
				<h2>Ranked editorial directions</h2>
			</div>
			<p>{candidates.scoring_note}</p>
		</div>

		<div class="candidate-list">
			{#each candidates.candidates as candidate}
				<article class:selected={candidate.id === selection.selected_candidate_id} class="candidate-card">
					<div class="rank">#{candidate.rank}</div>
					<div class="candidate-main">
						<div class="candidate-topline">
							<span class="pattern">{candidate.pattern.replaceAll("_", " ")}</span>
							<span class="score">{candidate.score}</span>
						</div>
						<h3>{candidate.claim}</h3>
						<p>{candidate.rationale}</p>
						<div class="tags">
							<span>{candidate.visual}</span>
							<span>{candidate.production_mode}</span>
							<span>{candidate.n} observations</span>
							{#if candidate.risk_penalty > 0}<span class="risk">−{candidate.risk_penalty} risk</span>{/if}
						</div>
						<div class="meters">
							{#each components as [key, label]}
								<div class="meter-row">
									<span>{label}</span>
									<div class="meter"><i style={`width:${pct(candidate.score_components[key])}`}></i></div>
									<b>{Math.round(candidate.score_components[key])}</b>
								</div>
							{/each}
						</div>
					</div>
				</article>
			{/each}
		</div>
	</section>

	<section class="quality-grid">
		<div>
			<p class="section-label">Selection attempts</p>
			<h2>Fallback is explicit</h2>
			{#each selection.attempts as attempt}
				<div class="attempt">
					<span>#{attempt.rank}</span>
					<strong>{attempt.candidate_id}</strong>
					<em class:pass={attempt.status === "PASS"}>{attempt.status}</em>
				</div>
			{/each}
		</div>
		<div>
			<p class="section-label">Quality gate</p>
			<h2>{evaluation.status}</h2>
			{#each evaluation.checks as check}
				<div class="check" class:failed={!check.ok}>
					<span>{check.ok ? "✓" : check.severity === "warning" ? "!" : "×"}</span>
					<div><strong>{check.name.replaceAll("_", " ")}</strong><p>{check.detail}</p></div>
				</div>
			{/each}
		</div>
		<div>
			<p class="section-label">Claim audit</p>
			<h2>{claimAudit.status}</h2>
			<p class="note">{claimAudit.note}</p>
			{#each claimAudit.reports as report}
				<div class="audit-block">
					<strong>{report.kind.replaceAll("_", " ")}</strong>
					{#each report.checks || [] as check}
						<div class="check" class:failed={!check.ok}>
							<span>{check.ok ? "✓" : "×"}</span>
							<div><strong>{check.field}</strong><p>stored {check.expected} · recomputed {check.actual}</p></div>
						</div>
					{/each}
				</div>
			{/each}
		</div>
	</section>
</section>

<style>
	.lab-shell { width: min(1180px, calc(100% - 40px)); margin: 0 auto; padding-bottom: 10vh; }
	.hero { max-width: 1020px; padding: 10vh 0 7vh; }
	.eyebrow, .section-label, .pattern, .tags, .status-row, .rank, .score { font-family: var(--font-mono); text-transform: uppercase; letter-spacing: .075em; font-size: .72rem; font-weight: 700; }
	.eyebrow, .section-label { color: #b7452a; }
	h1 { font-family: var(--font-serif); font-size: clamp(2.7rem, 7vw, 6.6rem); line-height: .96; letter-spacing: -.05em; margin: .2em 0 .4em; }
	h1 em { font-weight: 400; color: #b7452a; }
	.dek { max-width: 850px; font-size: clamp(1.08rem, 2vw, 1.42rem); line-height: 1.55; color: #5d5954; }
	.status-row { display: flex; flex-wrap: wrap; gap: .7rem; margin-top: 2rem; }
	.status-row span, .tags span { border: 1px solid #d8d1c7; border-radius: 999px; padding: .5rem .75rem; background: #fffdf8; }
	.status-row .pass { background: #e8f1e6; border-color: #b7cdb2; }
	.selected-panel { display: grid; grid-template-columns: 1fr auto; gap: 2rem; align-items: end; border: 1px solid #d8d1c7; border-radius: 18px; padding: clamp(1.3rem, 3vw, 2.5rem); background: #fffdf8; box-shadow: 0 20px 60px rgba(40, 33, 25, .05); }
	.selected-panel h2, .board-head h2, .quality-grid h2 { font-family: var(--font-serif); font-size: clamp(1.7rem, 3vw, 2.6rem); line-height: 1.08; margin: .35rem 0 .6rem; }
	.selected-panel a { display: inline-flex; align-items: center; min-height: 44px; font-family: var(--font-sans); font-weight: 750; color: #b7452a; text-decoration: none; white-space: nowrap; }
	.note, .board-head > p { color: #6b665f; line-height: 1.5; }
	.board { padding-top: 7rem; }
	.board-head { display: grid; grid-template-columns: 1fr minmax(260px, 430px); gap: 3rem; align-items: end; padding-bottom: 1.5rem; border-bottom: 1px solid #d8d1c7; }
	.candidate-list { display: grid; gap: 1rem; margin-top: 1.5rem; }
	.candidate-card { display: grid; grid-template-columns: 52px 1fr; gap: 1.25rem; padding: 1.5rem; border: 1px solid #ddd6cc; border-radius: 14px; background: rgba(255,253,248,.64); }
	.candidate-card.selected { border-color: #b7452a; box-shadow: inset 5px 0 0 #b7452a; }
	.rank { color: #837d75; padding-top: .2rem; }
	.candidate-topline { display: flex; justify-content: space-between; gap: 1rem; }
	.pattern { color: #777067; }
	.score { font-size: 1rem; color: #b7452a; }
	.candidate-main h3 { font-family: var(--font-serif); font-size: clamp(1.25rem, 2.3vw, 1.8rem); margin: .45rem 0; line-height: 1.18; }
	.candidate-main > p { margin: 0 0 1rem; color: #68625c; line-height: 1.45; }
	.tags { display: flex; gap: .45rem; flex-wrap: wrap; }
	.tags span { padding: .32rem .5rem; font-size: .63rem; }
	.tags .risk { color: #9a3e2b; }
	.meters { margin-top: 1.3rem; display: grid; gap: .45rem; }
	.meter-row { display: grid; grid-template-columns: 118px 1fr 34px; gap: .65rem; align-items: center; font-family: var(--font-sans); font-size: .72rem; }
	.meter { height: 6px; background: #ebe6dd; border-radius: 99px; overflow: hidden; }
	.meter i { display: block; height: 100%; background: #b7452a; border-radius: 99px; }
	.meter-row b { font-variant-numeric: tabular-nums; text-align: right; }
	.quality-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 3rem; padding-top: 7rem; }
	.audit-block { margin-top: 1rem; }
	.attempt, .check { display: grid; grid-template-columns: 36px 1fr auto; gap: .8rem; align-items: start; padding: .85rem 0; border-bottom: 1px solid #ddd6cc; font-family: var(--font-sans); }
	.attempt em { font-style: normal; font-family: var(--font-mono); font-size: .68rem; border: 1px solid #d8d1c7; border-radius: 999px; padding: .25rem .5rem; }
	.attempt em.pass { background: #e8f1e6; }
	.check { grid-template-columns: 28px 1fr; }
	.check > span { width: 22px; height: 22px; display: grid; place-items: center; border-radius: 50%; background: #e8f1e6; font-weight: 800; }
	.check.failed > span { background: #f5e7df; }
	.check p { margin: .25rem 0 0; color: #6b665f; font-size: .82rem; line-height: 1.4; }
	@media (max-width: 760px) {
		.lab-shell { width: min(100% - 28px, 680px); }
		.selected-panel, .board-head, .quality-grid { grid-template-columns: 1fr; }
		.candidate-card { grid-template-columns: 36px 1fr; padding: 1rem; }
		.meter-row { grid-template-columns: 100px 1fr 30px; }
	}
</style>
