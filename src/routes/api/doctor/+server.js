// src/routes/doctor/+page.server.js
import { db } from '$lib/server/db';
import { bloodPressureMeasurement } from '$lib/server/db/schema.js';
import { eq, desc } from 'drizzle-orm';

// Hvis I har en patient-tabel i jeres schema, skal den importeres her. 
// For nu laver vi en liste af patienter i koden, men henter de RIGTIGE målinger live!
const PATIENTS = [
    { id: 1, name: "Søren Hansen", age: 65, diagnosis: "Essentiel hypertension" },
    { id: 2, name: "Mette Jensen", age: 42, diagnosis: "Hvid kittel syndrom" }
];

export async function load({ url }) {
    // 1. Find ud af hvilken patient der er valgt i dropdown (standard: patient 1)
    const patientIdParam = url.searchParams.get('patient_id');
    const selectedId = patientIdParam ? Number(patientIdParam) : 1;
    
    const activePatient = PATIENTS.find(p => p.id === selectedId) || PATIENTS[0];

    try {
        // 2. Hent de RIGTIGE målinger for denne patient direkte fra databasen via Drizzle
        const measurements = await db.select()
            .from(bloodPressureMeasurement)
            .where(eq(bloodPressureMeasurement.patientId, activePatient.id))
            .orderBy(desc(bloodPressureMeasurement.id)); // Nyeste først (hvis I har et id eller tidsstempel)

        // 3. Beregn gennemsnit ud fra de rigtige målinger i databasen
        let avg_systolic = "-";
        let avg_diastolic = "-";
        
        if (measurements.length > 0) {
            const sumSys = measurements.reduce((acc, m) => acc + Number(m.systolic), 0);
            const sumDia = measurements.reduce((acc, m) => acc + Number(m.diastolic), 0);
            avg_systolic = Math.round((sumSys / measurements.length) * 10) / 10;
            avg_diastolic = Math.round((sumDia / measurements.length) * 10) / 10;
        }

        // 4. Bestem status ud fra gennemsnittet
        let status = "Ingen data";
        let statusColor = "gray";
        let statusText = "Der findes ingen blodtryksmålinger endnu.";

        if (avg_systolic !== "-") {
            if (avg_systolic >= 140 || avg_diastolic >= 90) {
                status = "Forhøjet blodtryk";
                statusColor = "#e67e22"; // Orange
                statusText = "Patientens blodtryk er forhøjet. Overvej medicinjustering.";
            } else {
                status = "Normalt blodtryk";
                statusColor = "#2ecc71"; // Grøn
                statusText = "Patientens blodtryk ser stabilt ud.";
            }
        }

        // Returner alt til frontenden (+page.svelte)
        return {
            patients: PATIENTS,
            activePatient,
            measurements,
            averages: { sys: avg_systolic, dia: avg_diastolic },
            status: { title: status, color: statusColor, text: statusText }
        };

    } catch (error) {
        console.error("Fejl ved hentning af lægedata:", error);
        return {
            patients: PATIENTS,
            activePatient,
            measurements: [],
            averages: { sys: "-", dia: "-" },
            status: { title: "Fejl", color: "red", text: "Kunne ikke hente data." }
        };
    }
}