<script>
	import { invalidateAll } from '$app/navigation';
	import { onMount } from 'svelte';

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

	let measurementGroups = $derived(groupMeasurements(filteredMeasurements));
	let totalAverage = $derived(calculateAverage(filteredMeasurements));

	onMount(() => {
		const interval = setInterval(() => {
			invalidateAll();
		}, 2000);

		return () => clearInterval(interval);
	});

	function formatDateParts(value) {
		if (!value || value === 'CURRENT_TIMESTAMP') {
			return { date: 'Ukendt dato', time: 'Ukendt tid' };
		}

		const date = new Date(value);
		if (Number.isNaN(date.getTime())) {
			return { date: value, time: 'Ukendt tid' };
		}

		return {
			date: date.toLocaleDateString('da-DK'),
			time: date.toLocaleTimeString('da-DK')
		};
	}

	function calculateAverage(measurements) {
		if (measurements.length === 0) {
			return null;
		}

		return {
			systolic: Math.round(
				measurements.reduce((sum, measurement) => sum + Number(measurement.systolic), 0) /
					measurements.length
			),
			diastolic: Math.round(
				measurements.reduce((sum, measurement) => sum + Number(measurement.diastolic), 0) /
					measurements.length
			),
			pulse: Math.round(
				measurements.reduce((sum, measurement) => sum + Number(measurement.pulse ?? 0), 0) /
					measurements.length
			)
		};
	}

	function groupMeasurements(measurements) {
		const groups = [];

		for (const measurement of measurements) {
			const key =
				measurement.measuredAt && measurement.measuredAt !== 'CURRENT_TIMESTAMP'
					? measurement.measuredAt
					: `measurement-${measurement.id}`;
			let group = groups.find((item) => item.id === key);

			if (!group) {
				group = {
					id: key,
					measuredAt: measurement.measuredAt,
					measurements: []
				};
				groups.push(group);
			}

			group.measurements.push(measurement);
		}

		return groups
			.map((group) => {
				const sortedMeasurements = group.measurements.sort((a, b) => Number(a.id) - Number(b.id));
				const session = parseSession(sortedMeasurements[0]?.note);

				return {
					...group,
					session,
					measurements: sortedMeasurements,
					average: calculateAverage(sortedMeasurements)
				};
			})
			.sort(compareMeasurementGroups)
			.map((group, index) => ({
				...group,
				sessionNumber: index + 1
			}));
	}

	function parseSession(note) {
		const match = note?.match(/^(Dag \d+)\s+(Morgen|Aften)/i);

		if (!match) {
			return { day: 'Ukendt dag', timeOfDay: 'Ukendt tidspunkt' };
		}

		return {
			day: match[1],
			timeOfDay: match[2]
		};
	}

	function formatMeasurementValue(measurement, key) {
		if (!measurement) return '-';

		return measurement[key] ?? '-';
	}

	function compareMeasurementGroups(a, b) {
		const dayDifference = getDayNumber(a.session.day) - getDayNumber(b.session.day);
		if (dayDifference !== 0) return dayDifference;

		const timeDifference =
			getTimeOfDayOrder(a.session.timeOfDay) - getTimeOfDayOrder(b.session.timeOfDay);
		if (timeDifference !== 0) return timeDifference;

		return new Date(a.measuredAt).getTime() - new Date(b.measuredAt).getTime();
	}

	function getDayNumber(day) {
		return Number(day.match(/\d+/)?.[0] ?? Number.MAX_SAFE_INTEGER);
	}

	function getTimeOfDayOrder(timeOfDay) {
		if (timeOfDay.toLowerCase() === 'morgen') return 1;
		if (timeOfDay.toLowerCase() === 'aften') return 2;

		return 3;
	}
</script>

<div class="doctor-page">
	<div class="container">
		<h1>Lægeside - Blodtryksdata</h1>

		<div class="card">
			<h2>Vælg patient</h2>
			<select id="patientSelect" bind:value={selectedPatientId}>
				<option value={null}>-- Vælg en patient --</option>
				{#each data.patients as p (p.id)}
					<option value={p.id}>{p.name}</option>
				{/each}
			</select>
		</div>

		{#if selectedPatientId !== null}
			<div class="card">
				<h2>
					Målinger for: {data.patients.find((p) => Number(p.id) === Number(selectedPatientId))
						?.name}
				</h2>

				{#if totalAverage}
					<section class="total-summary" aria-label="Samlet gennemsnit for alle dage">
						<div class="summary-heading">
							<span>Samlet gennemsnit</span>
							<strong>Alle dage</strong>
						</div>
						<table class="summary-table">
							<thead>
								<tr>
									<th>SYS</th>
									<th>DIA</th>
									<th>Puls</th>
								</tr>
							</thead>
							<tbody>
								<tr>
									<td>{totalAverage.systolic}</td>
									<td>{totalAverage.diastolic}</td>
									<td>{totalAverage.pulse}</td>
								</tr>
							</tbody>
						</table>
					</section>
				{/if}

				{#each measurementGroups as group (group.id)}
					<div class="measurement-group">
						<div class="measurement-meta">
							<div class="session-info">
								<span>Session {group.sessionNumber}</span>
								<strong>{group.session.day}</strong>
								<strong>{group.session.timeOfDay}</strong>
							</div>
							<div class="measurement-time">
								<div><strong>Dato:</strong> {formatDateParts(group.measuredAt).date}</div>
								<div><strong>Tid:</strong> {formatDateParts(group.measuredAt).time}</div>
							</div>
						</div>
						<table>
							<thead>
								<tr>
									<th class="row-label"></th>
									<th>1. måling</th>
									<th>2. måling</th>
									<th>3. måling</th>
									<th class="average-column">Gns.</th>
								</tr>
							</thead>
							<tbody>
								<tr>
									<th class="row-label">SYS</th>
									<td>{formatMeasurementValue(group.measurements[0], 'systolic')}</td>
									<td>{formatMeasurementValue(group.measurements[1], 'systolic')}</td>
									<td>{formatMeasurementValue(group.measurements[2], 'systolic')}</td>
									<td class="average-column"
										><strong>{formatMeasurementValue(group.average, 'systolic')}</strong></td
									>
								</tr>
								<tr>
									<th class="row-label">DIA</th>
									<td>{formatMeasurementValue(group.measurements[0], 'diastolic')}</td>
									<td>{formatMeasurementValue(group.measurements[1], 'diastolic')}</td>
									<td>{formatMeasurementValue(group.measurements[2], 'diastolic')}</td>
									<td class="average-column"
										><strong>{formatMeasurementValue(group.average, 'diastolic')}</strong></td
									>
								</tr>
								<tr>
									<th class="row-label">Puls</th>
									<td>{formatMeasurementValue(group.measurements[0], 'pulse')}</td>
									<td>{formatMeasurementValue(group.measurements[1], 'pulse')}</td>
									<td>{formatMeasurementValue(group.measurements[2], 'pulse')}</td>
									<td class="average-column"
										><strong>{formatMeasurementValue(group.average, 'pulse')}</strong></td
									>
								</tr>
							</tbody>
						</table>
					</div>
				{:else}
					<p>Ingen målinger fundet for denne patient.</p>
				{/each}
			</div>
		{:else}
			<div class="card">
				<p>Vælg venligst en patient fra listen ovenfor for at se målinger.</p>
			</div>
		{/if}
	</div>
</div>

<style>
	.doctor-page {
		min-height: 100vh;
		background-color: #f2f5f9;
		font-family: Arial, sans-serif;
		padding: 30px;
	}

	.container {
		max-width: 900px;
		margin: auto;
	}

	h1 {
		background-color: #1e3a5f;
		color: white;
		padding: 20px;
		border-radius: 10px;
		font-size: 32px;
		font-weight: 700;
	}

	.card {
		background-color: white;
		padding: 20px;
		margin-top: 20px;
		border-radius: 10px;
		box-shadow: 0 3px 8px rgba(0, 0, 0, 0.1);
	}

	h2 {
		margin-bottom: 14px;
		font-size: 22px;
		font-weight: 700;
	}

	select {
		width: 100%;
		padding: 10px;
		margin-top: 8px;
		margin-bottom: 15px;
		font-size: 15px;
	}

	.total-summary {
		background: linear-gradient(135deg, #1e3a5f, #2c5282);
		border-radius: 10px;
		color: white;
		margin: 16px 0 22px;
		padding: 18px;
	}

	.summary-heading {
		align-items: baseline;
		display: flex;
		justify-content: space-between;
		gap: 12px;
		margin-bottom: 14px;
	}

	.summary-heading span {
		color: #bfdbfe;
		font-size: 13px;
		font-weight: 700;
		letter-spacing: 0.04em;
		text-transform: uppercase;
	}

	.summary-heading strong {
		font-size: 20px;
	}

	.summary-table {
		border-collapse: separate;
		border-spacing: 0;
		margin-top: 0;
		overflow: hidden;
	}

	.summary-table th,
	.summary-table td {
		background-color: rgba(255, 255, 255, 0.12);
		border: 0;
		color: white;
		text-align: center;
	}

	.summary-table th {
		color: #dbeafe;
		font-size: 13px;
		text-transform: uppercase;
	}

	.summary-table td {
		font-size: 28px;
		font-weight: 800;
	}

	.measurement-group {
		margin-top: 18px;
		padding: 16px;
		border: 1px solid #e5e7eb;
		border-radius: 8px;
	}

	.measurement-meta {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 12px;
		margin-bottom: 12px;
		color: #334155;
		font-size: 15px;
	}

	.session-info {
		display: flex;
		align-items: center;
		gap: 10px;
		flex-wrap: wrap;
	}

	.session-info span {
		color: #64748b;
		font-weight: 700;
		text-transform: uppercase;
		letter-spacing: 0.04em;
		font-size: 12px;
	}

	.session-info strong {
		background-color: #dbeafe;
		border-radius: 999px;
		color: #1e3a5f;
		padding: 5px 10px;
	}

	.measurement-time {
		display: grid;
		gap: 4px;
		text-align: right;
	}

	table {
		width: 100%;
		border-collapse: collapse;
	}

	th,
	td {
		border: 1px solid #ddd;
		padding: 10px;
		text-align: center;
	}

	th {
		background-color: #dbeafe;
	}

	.row-label {
		width: 90px;
		text-align: left;
	}

	.average-column {
		background-color: #eef6ff;
	}

	@media (max-width: 700px) {
		.summary-heading {
			align-items: flex-start;
			flex-direction: column;
		}
	}
</style>
