import { POST as saveMeasurements } from '../save-measurements/+server.js';

export async function POST(event) {
	return saveMeasurements(event);
}
