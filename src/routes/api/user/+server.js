import { json } from '@sveltejs/kit';
import { db } from '$lib/server/db';
import { patient, user } from '$lib/server/db/schema.js';
import bcrypt from 'bcryptjs';
import { eq } from 'drizzle-orm'; // Tilføjet til filtrering i databasen

export async function POST({ request }) {
	try {
		const { username, password, role } = await request.json();

		// 1. Basal validering
		if (!username || !password || !role) {
			return json(
				{ error: 'Alle felter (brugernavn, adgangskode og rolle) skal udfyldes' },
				{ status: 400 }
			);
		}

		// 2. Hash adgangskoden
		const hashedPass = await bcrypt.hash(password, 10);

		// 3. Indsæt brugeren i databasen
		const createdUserArray = await db
			.insert(user)
			.values({
				username,
				password: hashedPass,
				role
			})
			.returning();

		const createdUser = createdUserArray[0];

		// Patient-login skal også have en række i patient-tabellen,
		// fordi lægesiden og målingerne bruger patient.id.
		if (role === 'patient') {
			await db.insert(patient).values({
				userId: createdUser.id,
				name: username
			});
		}

		return json({ success: true, user: createdUser }, { status: 201 });
	} catch (error) {
		console.error('Databasefejl ved oprettelse af bruger:', error);

		if (error.message?.includes('UNIQUE') || error.code === '23505') {
			return json({ error: 'Brugernavnet er allerede taget' }, { status: 409 });
		}

		return json(
			{ error: 'Der opstod en intern fejl i databasen: ' + error.message },
			{ status: 500 }
		);
	}
}

// HENTER ALLE BRUGERE FRA DATABASEN SOM ER PATIENTER
export async function GET() {
	try {
		const patienter = await db
			.select({
				id: user.id,
				navn: user.username
			})
			.from(user)
			.where(eq(user.role, 'patient'));

		return json(patienter, { status: 200 });
	} catch (error) {
		console.error('Databasefejl ved hentning af patienter:', error);
		return json({ error: 'Kunne ikke hente patienter fra databasen' }, { status: 500 });
	}
}
