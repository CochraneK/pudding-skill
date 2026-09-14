<script>
	import { onMount } from 'svelte';
	import { initLanguage, language, setLanguage } from '$lib/language.js';

	onMount(initLanguage);
</script>

<div class="language-toggle" role="group" aria-label={$language === 'zh' ? '语言切换' : 'Language switcher'}>
	<button type="button" class:active={$language === 'zh'} aria-pressed={$language === 'zh'} onclick={() => setLanguage('zh')}>中文</button>
	<span aria-hidden="true">/</span>
	<button type="button" class:active={$language === 'en'} aria-pressed={$language === 'en'} onclick={() => setLanguage('en')}>EN</button>
</div>

<style>
	.language-toggle {
		display: inline-flex;
		align-items: center;
		gap: 0.1rem;
		padding: 0 0.25rem;
		min-height: 46px;
		border: 1px solid currentColor;
		border-radius: 999px;
		font: 700 0.72rem/1 var(--font-sans);
		letter-spacing: 0.04em;
	}

	button {
		appearance: none;
		border: 0;
		min-width: 44px;
		min-height: 44px;
		padding: 0.55rem 0.45rem;
		background: transparent;
		color: inherit;
		font: inherit;
		font-family: "Noto Sans CJK SC", "PingFang SC", "Microsoft YaHei", var(--font-sans);
		cursor: pointer;
		opacity: 0.45;
	}

	button.active {
		opacity: 1;
	}

	button:focus-visible {
		outline: 2px solid currentColor;
		outline-offset: 0;
		border-radius: 999px;
	}

	span {
		opacity: 0.35;
	}
</style>
