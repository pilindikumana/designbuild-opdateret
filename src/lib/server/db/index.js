import { drizzle } from 'drizzle-orm/better-sqlite3';
import Database from 'better-sqlite3';
import * as schema from './schema.js';

// Dette opretter en lokal fil i dit projekt, der hedder 'sqlite.db'
const sqlite = new Database('sqlite.db'); 
export const db = drizzle(sqlite, { schema });