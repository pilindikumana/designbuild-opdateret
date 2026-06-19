import { json } from '@sveltejs/kit';
import { env } from '$env/dynamic/private';
import { db } from '$lib/server/db';
import { bloodPressureMeasurement, patient } from '$lib/server/db/schema.js';
import { eq } from 'drizzle-orm';
import jwt from 'jsonwebtoken';

function parseNumber(value) {
	const number = Number(value);
	return Number.isFinite(number) ? number : null;
}

async function getPatientIdFromSession(cookies) {
	const token = cookies.get('session');
	if (!token) return null;

	try {
		const secret = env.JWT_SECRET || 'super-secret-fallback-key-dtu-project';
		const payload = jwt.verify(token, secret);

		if (payload.role !== 'patient') return null;

		const rows = await db
			.select({ id: patient.id })
			.from(patient)
			.where(eq(patient.userId, payload.userId))
			.limit(1);

		return rows[0]?.id ?? null;
	} catch {
		return null;
	}
}

export async function POST({ request, cookies }) {
	try {
		const body = await request.json();
		const sessionPatientId = await getPatientIdFromSession(cookies);
		const patientId = sessionPatientId ?? parseNumber(body.patientId);
		const systolic = parseNumber(body.systolic);
		const diastolic = parseNumber(body.diastolic);
		const pulse = parseNumber(body.pulse);

		if (!patientId || !systolic || !diastolic) {
			return json(
				{ error: 'Patient, systolisk og diastolisk værdi skal være gyldige tal' },
				{ status: 400 }
			);
		}

		const patientExists = await db
			.select({ id: patient.id })
			.from(patient)
			.where(eq(patient.id, patientId))
			.limit(1);

		if (!patientExists[0]) {
			return json({ error: 'Patienten findes ikke i databasen' }, { status: 404 });
		}

		const inserted = await db
			.insert(bloodPressureMeasurement)
			.values({
				patientId,
				systolic,
				diastolic,
				pulse
			})
			.returning();

		return json({ success: true, measurement: inserted[0] }, { status: 201 });
	} catch (error) {
		console.error('Fejl ved gemning af målinger:', error);
		return json({ error: error.message }, { status: 500 });
	}
}
