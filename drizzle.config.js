import { defineConfig } from 'drizzle-kit';

export default defineConfig({
	schema: './src/lib/server/db/schema.js',
	out: './drizzle',
	dialect: 'sqlite',
	dbCredentials: {
		url: 'sqlite.db' // Sørg for at dette matcher navnet i din index.js
	}
});
