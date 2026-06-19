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

function parseMeasurement(measurement) {
	const systolic = parseNumber(measurement.systolic);
	const diastolic = parseNumber(measurement.diastolic);
	const pulse = parseNumber(measurement.pulse);

	if (!systolic || !diastolic) return null;

	return {
		systolic,
		diastolic,
		pulse,
		note: measurement.note ?? null
	};
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
		const measurements = Array.isArray(body.measurements)
			? body.measurements.map(parseMeasurement).filter(Boolean)
			: [];

		if (measurements.length === 0) {
			const singleMeasurement = parseMeasurement(body);
			if (singleMeasurement) measurements.push(singleMeasurement);
		}

		if (!patientId || measurements.length === 0) {
			return json({ error: 'Patient og mindst én måling skal være gyldige' }, { status: 400 });
		}

		const patientExists = await db
			.select({ id: patient.id })
			.from(patient)
			.where(eq(patient.id, patientId))
			.limit(1);

		if (!patientExists[0]) {
			return json({ error: 'Patienten findes ikke i databasen' }, { status: 404 });
		}

		const now = new Date().toISOString();
		const inserted = await db
			.insert(bloodPressureMeasurement)
			.values(
				measurements.map((measurement) => ({
					...measurement,
					patientId,
					measuredAt: now,
					createdAt: now
				}))
			)
			.returning();

		return json({ success: true, measurements: inserted }, { status: 201 });
	} catch (error) {
		console.error('Fejl ved gemning af målinger:', error);
		return json({ error: error.message }, { status: 500 });
	}
}
