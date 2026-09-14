import { browser } from '$app/environment';
import { writable } from 'svelte/store';

const store = writable('zh');
let initialized = false;

function normalize(value) {
	return value === 'en' ? 'en' : 'zh';
}

function applyDocumentLanguage(value) {
	if (!browser) return;
	document.documentElement.lang = value === 'zh' ? 'zh-CN' : 'en';
}

export function initLanguage() {
	if (!browser || initialized) return;
	initialized = true;

	const url = new URL(window.location.href);
	const queryLanguage = url.searchParams.get('lang');
	const storedLanguage = window.localStorage.getItem('pudding-language');
	const next = normalize(queryLanguage || storedLanguage || 'zh');
	store.set(next);
	applyDocumentLanguage(next);
}

export function setLanguage(value) {
	const next = normalize(value);
	store.set(next);
	applyDocumentLanguage(next);

	if (!browser) return;
	window.localStorage.setItem('pudding-language', next);
	const url = new URL(window.location.href);
	url.searchParams.set('lang', next);
	window.history.replaceState({}, '', url);
}

export const language = {
	subscribe: store.subscribe
};
