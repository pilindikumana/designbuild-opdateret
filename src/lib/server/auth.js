import { redirect } from '@sveltejs/kit';
import { env } from '$env/dynamic/private';
import jwt from 'jsonwebtoken';

export function getSessionUser(cookies) {
	const token = cookies.get('session');
	if (!token) return null;

	try {
		const secret = env.JWT_SECRET || 'super-secret-fallback-key-dtu-project';
		return jwt.verify(token, secret);
	} catch {
		return null;
	}
}

export function requireRole(cookies, role) {
	const user = getSessionUser(cookies);

	if (!user) {
		throw redirect(303, '/login');
	}

	if (user.role !== role) {
		throw redirect(303, user.role === 'patient' ? '/patient' : '/doctor');
	}

	return user;
}
