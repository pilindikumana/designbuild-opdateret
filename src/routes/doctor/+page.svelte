<script>
	// Vi modtager både patienter og målinger fra serveren
	let { data } = $props();

	let selectedPatientId = $state(null);

	$effect(() => {
		if (selectedPatientId === null && data.patients.length > 0) {
			selectedPatientId = data.patients[0].id;
		}
	});

	// Filtrer målingerne så kun dem for den valgte patient vises
	let filteredMeasurements = $derived(
		data.measurements.filter((m) => Number(m.patientId) === Number(selectedPatientId))
	);
</script>

<div class="p-8">
	<h1 class="text-2xl font-bold mb-6">Lægeoversigt</h1>

	<div class="mb-8">
		<label for="patientSelect" class="block font-semibold mb-2">Vælg patient:</label>
		<select id="patientSelect" bind:value={selectedPatientId} class="border p-2 rounded w-64">
			<option value={null}>-- Vælg en patient --</option>
			{#each data.patients as p (p.id)}
				<option value={p.id}>{p.name} (ID: {p.id})</option>
			{/each}
		</select>
	</div>

	{#if selectedPatientId !== null}
		<h2 class="text-xl font-semibold mb-4">
			Målinger for: {data.patients.find((p) => Number(p.id) === Number(selectedPatientId))?.name}
		</h2>

		<table class="w-full border-collapse border border-gray-300">
			<thead>
				<tr class="bg-gray-100">
					<th class="border p-2">SYS</th>
					<th class="border p-2">DIA</th>
					<th class="border p-2">Puls</th>
					<th class="border p-2">Dato</th>
				</tr>
			</thead>
			<tbody>
				{#each filteredMeasurements as m (m.id)}
					<tr>
						<td class="border p-2 text-center">{m.systolic}</td>
						<td class="border p-2 text-center">{m.diastolic}</td>
						<td class="border p-2 text-center">{m.pulse}</td>
						<td class="border p-2 text-center">
							{m.measuredAt ? new Date(m.measuredAt).toLocaleString('da-DK') : 'Ukendt dato'}
						</td>
					</tr>
				{:else}
					<tr
						><td colspan="4" class="p-4 text-center">Ingen målinger fundet for denne patient.</td
						></tr
					>
				{/each}
			</tbody>
		</table>
	{:else}
		<p class="text-gray-500 italic">
			Vælg venligst en patient fra listen ovenfor for at se målinger.
		</p>
	{/if}
</div>
