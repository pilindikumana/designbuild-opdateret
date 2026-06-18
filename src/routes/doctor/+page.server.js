import { db } from '$lib/server/db';
import { bloodPressureMeasurement, patient } from '$lib/server/db/schema.js';

export async function load() {
    // Hent alle patienter
    const allPatients = await db.select().from(patient);
    
    // Hent alle målinger
    const allMeasurements = await db.select().from(bloodPressureMeasurement);

    return {
        patients: allPatients,
        measurements: allMeasurements
    };
}