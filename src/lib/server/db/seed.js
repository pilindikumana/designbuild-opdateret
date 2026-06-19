import { db } from './index.js'; // Sørg for at stien peger på din db-instans
import { patient } from './schema.js';

async function seed() {
	try {
		await db.insert(patient).values({
			id: 1,
			name: 'Test Patient',
			age: 45,
			cpr: '010101-0000',
			diagnosis: 'Test-diagnose'
		});
		console.log('Patient 1 er nu oprettet i databasen!');
	} catch (e) {
		console.log('Kunne ikke oprette patient (måske findes den allerede?):', e.message);
	}
}

seed();
