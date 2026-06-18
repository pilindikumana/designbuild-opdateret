import { json } from '@sveltejs/kit';
import { db } from '$lib/server/db';
import { bloodPressureMeasurement } from '$lib/server/db/schema.js';

export async function POST({ request }) {
    try {
        const { systolic, diastolic, pulse, patientId } = await request.json();
        
        // Gemmer målingen og linker den til det valgte patientId
        await db.insert(bloodPressureMeasurement).values({
            patientId: Number(patientId), 
            systolic: Number(systolic),
            diastolic: Number(diastolic),
            pulse: Number(pulse)
        });

        return json({ success: true });
    } catch (error) {
        return json({ error: error.message }, { status: 500 });
    }
}