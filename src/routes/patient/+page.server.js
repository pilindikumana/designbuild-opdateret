import { requireRole } from '$lib/server/auth.js';

export function load({ cookies }) {
	requireRole(cookies, 'patient');

	return {};
}
