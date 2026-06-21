import { db } from '$lib/server/db';
import { bloodPressureMeasurement, patient } from '$lib/server/db/schema.js';
import { requireRole } from '$lib/server/auth.js';
import { desc } from 'drizzle-orm';

export async function load({ cookies }) {
	requireRole(cookies, 'sundhedsprofessionel');

	// Hent alle patienter
	const allPatients = await db.select().from(patient);

	// Hent alle målinger
	const allMeasurements = await db
		.select()
		.from(bloodPressureMeasurement)
		.orderBy(desc(bloodPressureMeasurement.id));

	return {
		patients: allPatients,
		measurements: allMeasurements
	};
}
