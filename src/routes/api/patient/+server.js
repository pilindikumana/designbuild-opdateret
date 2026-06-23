import { SerialPort } from 'serialport';
import { ReadlineParser } from '@serialport/parser-readline';

const ARDUINO_PORT = '/dev/cu.usbmodem101';

export async function POST() {
	const encoder = new TextEncoder();
	const stream = new TransformStream();
	const writer = stream.writable.getWriter();

	const port = new SerialPort({
		path: ARDUINO_PORT,
		baudRate: 9600,
		autoOpen: false
	});

	const parser = port.pipe(new ReadlineParser({ delimiter: '\r\n' }));

	port.open((err) => {
		if (err) {
			console.error('Kunne ikke åbne porten:', err.message);
			writer
				.write(encoder.encode('FEJL:Kunne ikke forbinde til Arduino\n'))
				.then(() => writer.close());
			return;
		}

		console.log('Porten er åben! Venter 2 sekunder på boot...');

		setTimeout(() => {
			console.log('Sender START...');
			port.write('START\n', (writeErr) => {
				if (writeErr) {
					console.error('Skrivefejl:', writeErr.message);
					port.close();
					writer.write(encoder.encode('FEJL:Kunne ikke sende signal\n')).then(() => writer.close());
				}
			});
		}, 2000);
	});

	parser.on('data', async (data) => {
		const besked = data.trim();
		console.log('Fra Arduino -> Live Stream:', besked);

		if (besked === 'FÆRDIG') {
			port.close();
			await writer.write(encoder.encode('STATUS:FÆRDIG\n'));
			await writer.close();
		} else {
			await writer.write(encoder.encode(besked + '\n'));
		}
	});

	port.on('error', async (err) => {
		console.error('Serialport fejl:', err.message);
		if (port.isOpen) port.close();
		try {
			await writer.write(encoder.encode('FEJL:Seriel fejl\n'));
			await writer.close();
		} catch {
			console.log('Streamen var allerede lukket af klienten.');
		}
	});

	return new Response(stream.readable, {
		headers: {
			'Content-Type': 'text/plain; charset=utf-8',
			'Transfer-Encoding': 'chunked'
		}
	});
}
