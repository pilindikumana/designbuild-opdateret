import { sqliteTable, text, integer } from 'drizzle-orm/sqlite-core';

// 1. User-tabel (Til login og roller)
export const user = sqliteTable('user', {
	id: integer('id').primaryKey({ autoIncrement: true }),
	username: text('username').notNull().unique(),
	password: text('password').notNull(),
	role: text('role').notNull(), // 'patient', 'sundhedsprofessionel' (læge)
	createdAt: text('created_at').default('CURRENT_TIMESTAMP')
});

// 2. Patient-tabel (Stamdata om patienten)
export const patient = sqliteTable('patient', {
	id: integer('id').primaryKey({ autoIncrement: true }),
	userId: integer('user_id').references(() => user.id, { onDelete: 'SET NULL' }),
	name: text('name').notNull(),
	age: integer('age'),
	cpr: text('cpr'),
	phone: text('phone'),
	diagnosis: text('diagnosis'),
	createdAt: text('created_at').default('CURRENT_TIMESTAMP')
});

// 3. Blodtryksmålinger (Forbundet til Patient-tabellen)
export const bloodPressureMeasurement = sqliteTable('blood_pressure_measurement', {
	id: integer('id').primaryKey({ autoIncrement: true }),
	patientId: integer('patient_id')
		.notNull()
		.references(() => patient.id, { onDelete: 'CASCADE' }),
	systolic: integer('systolic').notNull(),
	diastolic: integer('diastolic').notNull(),
	pulse: integer('pulse'),
	note: text('note'),
	measuredAt: text('measured_at').default('CURRENT_TIMESTAMP'),
	createdAt: text('created_at').default('CURRENT_TIMESTAMP')
});

// 4. Feedback-tabel (Lægens beskeder til patienten)
export const feedback = sqliteTable('feedback', {
	id: integer('id').primaryKey({ autoIncrement: true }),
	patientId: integer('patient_id')
		.notNull()
		.references(() => patient.id, { onDelete: 'CASCADE' }),
	authorUserId: integer('author_user_id').references(() => user.id, { onDelete: 'SET NULL' }),
	message: text('message').notNull(),
	createdAt: text('created_at').default('CURRENT_TIMESTAMP')
});
