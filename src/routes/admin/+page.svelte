<script>
	// Fjernet ubrugt import af createSubscriber for at undgå advarsler
	let username = $state('');
	let password = $state('');
	let role = $state('');

	const createUser = async () => {
		if (!role) {
			alert('Husk at vælge en rolle!');
			return;
		}

		try {
			const response = await fetch('/api/user', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({ username, password, role })
			});

			const data = await response.json();

			if (response.ok) {
				alert('Bruger oprettet succesfuldt!');
				// Nulstil felterne efter succes
				username = '';
				password = '';
				role = '';
			} else {
				// Hvis serveren sender en fejlbesked med ({ error: '...' })
				alert('Fejl ved oprettelse: ' + (data.error || 'Ukendt fejl på serveren'));
			}
		} catch (error) {
			console.error('Netværksfejl:', error);
			alert('Kunne ikke oprette forbindelse til serveren.');
		}
	};
</script>

<div
	class="min-h-screen w-full flex items-center justify-center bg-linear-to-tr from-[#93c5fd] via-[#bfdbfe] to-[#e0f2fe] px-4 relative"
>
	<div
		class="w-full max-w-md bg-white/20 backdrop-blur-md rounded-2xl p-8 border border-white/40 shadow-2xl relative text-slate-800"
	>
		<button
			class="absolute top-4 right-4 text-slate-600 hover:text-slate-900 transition-colors"
			aria-label="Luk"
		>
			<svg
				xmlns="http://www.w3.org/2000/svg"
				class="h-5 w-5"
				fill="none"
				viewBox="0 0 24 24"
				stroke="currentColor"
			>
				<path
					stroke-linecap="round"
					stroke-linejoin="round"
					stroke-width="2"
					d="M6 18L18 6M6 6l12 12"
				/>
			</svg>
		</button>

		<h2 class="text-3xl font-semibold text-center mb-8 tracking-wide text-slate-800">
			Opret bruger
		</h2>

		<div class="flex flex-col gap-6">
			<div
				class="relative border-b border-slate-400 focus-within:border-slate-800 transition-colors py-1"
			>
				<label
					class="block text-xs uppercase tracking-wider text-slate-600 mb-1"
					for="admin-username">Brugernavn</label
				>
				<div class="flex items-center justify-between">
					<input
						id="admin-username"
						type="text"
						bind:value={username}
						placeholder="Indtast brugernavn"
						class="bg-transparent w-full text-slate-800 placeholder-slate-400 outline-none pr-4 text-sm"
					/>
					<svg
						xmlns="http://www.w3.org/2000/svg"
						class="h-5 w-5 text-slate-500"
						fill="none"
						viewBox="0 0 24 24"
						stroke="currentColor"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
						/>
					</svg>
				</div>
			</div>

			<div
				class="relative border-b border-slate-400 focus-within:border-slate-800 transition-colors py-1"
			>
				<label
					class="block text-xs uppercase tracking-wider text-slate-600 mb-1"
					for="admin-password">Adgangskode</label
				>
				<div class="flex items-center justify-between">
					<input
						id="admin-password"
						type="password"
						bind:value={password}
						placeholder="Indtast adgangskode"
						class="bg-transparent w-full text-slate-800 placeholder-slate-400 outline-none pr-4 text-sm"
					/>
					<svg
						xmlns="http://www.w3.org/2000/svg"
						class="h-5 w-5 text-slate-500"
						fill="none"
						viewBox="0 0 24 24"
						stroke="currentColor"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
						/>
					</svg>
				</div>
			</div>

			<div
				class="relative border-b border-slate-400 focus-within:border-slate-800 transition-colors py-1"
			>
				<label class="block text-xs uppercase tracking-wider text-slate-600 mb-1" for="admin-role"
					>Vælg systemrolle</label
				>
				<select
					id="admin-role"
					bind:value={role}
					class="bg-transparent w-full text-slate-800 outline-none text-sm cursor-pointer appearance-none pr-4 py-1"
				>
					<option value="" disabled>Vælg venligst en rolle...</option>
					<option value="patient" class="text-slate-800">Patient</option>
					<option value="sundhedsprofessionel" class="text-slate-800">Sundhedsprofessionel</option>
				</select>
			</div>

			<button
				class="mt-4 w-full bg-[#bae6fd] hover:bg-[#7dd3fc] text-slate-800 font-medium py-3 rounded-lg transition-colors shadow-lg disabled:opacity-50"
				onclick={createUser}
				disabled={!role || !username || !password}
			>
				Opret bruger
			</button>
		</div>
	</div>
</div>
