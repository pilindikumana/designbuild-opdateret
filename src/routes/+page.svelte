<script>
	import { resolve } from '$app/paths';
</script>

<div
	class="min-h-screen w-full flex flex-col items-center justify-center bg-gradient-to-tr from-[#93c5fd] via-[#bfdbfe] to-[#e0f2fe] px-4 text-center text-slate-800"
>
	<div
		class="w-full max-w-lg bg-white/20 backdrop-blur-md rounded-2xl p-10 border border-white/40 shadow-2xl flex flex-col items-center gap-6"
	>
		<div class="flex flex-col gap-2">
			<h1 class="text-4xl font-bold tracking-wide text-slate-900">Blodtryksportalen</h1>
			<p class="text-sm uppercase tracking-widest text-slate-600 font-medium">
				Digitalt Sundhedsværktøj
			</p>
		</div>

		<div class="w-16 h-1 bg-slate-400/50 rounded"></div>

		<p class="text-slate-700 max-w-sm leading-relaxed">
			Velkommen til din personlige blodtryksmåler. Log ind for at registrere målinger.
		</p>

		<a
			href={resolve('/login')}
			class="mt-4 w-full max-w-xs bg-[#bae6fd] hover:bg-[#7dd3fc] text-slate-800 font-semibold py-3 rounded-lg transition-colors shadow-lg block text-center"
		>
			Gå til Login
		</a>
	</div>
</div>
