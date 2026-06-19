import { json } from '@sveltejs/kit';
import bcrypt from 'bcryptjs';
import { db } from '$lib/server/db';
import { patient, user } from '$lib/server/db/schema.js';
import { eq } from 'drizzle-orm';
import jwt from 'jsonwebtoken';
import { env } from '$env/dynamic/private';

export async function POST({ request, cookies }) {
	try {
		const { username, password } = await request.json();

		if (!username || !password) {
			return json({ error: 'Brugernavn og adgangskode skal udfyldes' }, { status: 400 });
		}

		// Find brugeren i databasen ved hjælp af standard Drizzle select
		const rows = await db.select().from(user).where(eq(user.username, username)).limit(1);
		const userData = rows[0];

		if (!userData) {
			return json({ error: 'Forkert brugernavn eller adgangskode' }, { status: 401 });
		}

		// Tjek om adgangskoden matcher det krypterede hash
		const isPasswordValid = await bcrypt.compare(password, userData.password);
		if (!isPasswordValid) {
			return json({ error: 'Forkert brugernavn eller adgangskode' }, { status: 401 });
		}

		let patientId = null;

		if (userData.role === 'patient') {
			const patientRows = await db
				.select()
				.from(patient)
				.where(eq(patient.userId, userData.id))
				.limit(1);

			if (patientRows[0]) {
				patientId = patientRows[0].id;
			} else {
				const createdPatient = await db
					.insert(patient)
					.values({
						userId: userData.id,
						name: userData.username
					})
					.returning();

				patientId = createdPatient[0].id;
			}
		}

		// Generer JWT Token. Vi bruger en fallback-streng hvis .env ikke er sat op endnu
		const secret = env.JWT_SECRET || 'super-secret-fallback-key-dtu-project';
		const token = jwt.sign(
			{ userId: userData.id, username: userData.username, role: userData.role, patientId },
			secret,
			{ expiresIn: '1h' }
		);

		// Gem session-cookien i browseren
		cookies.set('session', token, {
			path: '/',
			httpOnly: true,
			sameSite: 'strict',
			maxAge: 60 * 60 // 1 time
		});

		return json({ message: 'Login successful', role: userData.role, patientId }, { status: 200 });
	} catch (error) {
		console.error('Login fejl:', error);
		return json({ error: 'Der opstod en fejl på serveren under login' }, { status: 500 });
	}
}
