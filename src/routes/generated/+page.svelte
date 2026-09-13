<script>
	import Meta from "$components/Meta.svelte";
	import AutoStory from "$components/AutoStory.svelte";
	import bundle from "$data/auto-story.json";
</script>

<Meta title="Generated baseline story" description={bundle.spec.primary_insight} />
<AutoStory {bundle} />
