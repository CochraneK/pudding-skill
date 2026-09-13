<script>
	let {
		title = "Pudding Scrolly",
		description = "An editorial data-storytelling skill and Svelte starter.",
		url = "",
		keywords = "data visualization, scrollytelling, data journalism",
		siteName = "Pudding Scrolly",
		author = "",
		image = ""
	} = $props();
</script>

<svelte:head>
	<title>{title}</title>
	<meta name="description" content={description} />
	<meta name="news_keywords" content={keywords} />
	{#if author}<meta name="author" content={author} />{/if}

	<meta property="og:title" content={title} />
	<meta property="og:site_name" content={siteName} />
	<meta property="og:description" content={description} />
	<meta property="og:type" content="article" />
	<meta property="og:locale" content="en_US" />
	{#if url}<meta property="og:url" content={url} />{/if}
	{#if image}<meta property="og:image" content={image} />{/if}

	<meta name="twitter:card" content={image ? "summary_large_image" : "summary"} />
	<meta name="twitter:title" content={title} />
	<meta name="twitter:description" content={description} />
	{#if image}<meta name="twitter:image" content={image} />{/if}

	<meta name="robots" content="max-image-preview:large" />
	{#if url}<link rel="canonical" href={url} />{/if}
</svelte:head>
