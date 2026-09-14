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
		gap: 0.45rem;
		padding: 0.3rem 0.55rem;
		border: 1px solid currentColor;
		border-radius: 999px;
		font: 700 0.72rem/1 var(--font-sans);
		letter-spacing: 0.04em;
	}

	button {
		appearance: none;
		border: 0;
		padding: 0.3rem 0.25rem;
		background: transparent;
		color: inherit;
		font: inherit;
		cursor: pointer;
		opacity: 0.45;
	}

	button.active {
		opacity: 1;
	}

	button:focus-visible {
		outline: 2px solid currentColor;
		outline-offset: 2px;
	}

	span {
		opacity: 0.35;
	}
</style>
