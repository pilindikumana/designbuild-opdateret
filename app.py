from flask import Flask, request, redirect, jsonify
from html import escape

from database import (
    init_database,
    seed_database,
    get_all_patients,
    get_patient_measurements,
    get_patient_feedback,
    add_feedback,
    add_measurement,
)

app = Flask(__name__)

init_database()
seed_database()


def find_patient(patient_id):
    patients = get_all_patients()

    for patient in patients:
        if patient["id"] == patient_id:
            return patient

    return patients[0] if patients else None


def calculate_average(patient):
    measurements = get_patient_measurements(patient["id"])

    if len(measurements) == 0:
        return "-", "-"

    avg_systolic = sum(m["systolic"] for m in measurements) / len(measurements)
    avg_diastolic = sum(m["diastolic"] for m in measurements) / len(measurements)

    return round(avg_systolic, 1), round(avg_diastolic, 1)


def get_status(avg_systolic, avg_diastolic):
    if avg_systolic == "-":
        return "Ingen data", "gray", "Der findes ingen blodtryksmålinger endnu."

    if avg_systolic >= 140 or avg_diastolic >= 90:
        return "Forhøjet blodtryk", "orange", "Patientens blodtryk er forhøjet. Lægen bør give feedback."

    return "Normalt blodtryk", "green", "Patientens blodtryk ser stabilt ud."


@app.route("/")
def home():
    return redirect("/doctor")


@app.route("/doctor")
def doctor_page():
    patient_id = request.args.get("patient_id", 1, type=int)

    patients = get_all_patients()
    patient = find_patient(patient_id)

    if patient is None:
        return "Ingen patienter fundet i databasen."

    measurements = get_patient_measurements(patient["id"])
    feedback_list = get_patient_feedback(patient["id"])

    avg_systolic, avg_diastolic = calculate_average(patient)
    status, status_color, status_text = get_status(avg_systolic, avg_diastolic)

    html = f"""
    <!DOCTYPE html>
    <html lang="da">
    <head>
        <meta charset="UTF-8">
        <title>Lægeside</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f2f5f9;
                margin: 0;
                padding: 30px;
            }}
            .container {{
                max-width: 900px;
                margin: auto;
            }}
            h1 {{
                background-color: #1e3a5f;
                color: white;
                padding: 20px;
                border-radius: 10px;
            }}
            .card {{
                background-color: white;
                padding: 20px;
                margin-top: 20px;
                border-radius: 10px;
                box-shadow: 0 3px 8px rgba(0,0,0,0.1);
            }}
            select, input, textarea, button {{
                width: 100%;
                padding: 10px;
                margin-top: 8px;
                margin-bottom: 15px;
                font-size: 15px;
            }}
            button {{
                background-color: #1e3a5f;
                color: white;
                border: none;
                border-radius: 6px;
                cursor: pointer;
            }}
            button:hover {{
                background-color: #2c5282;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 10px;
            }}
            th, td {{
                border: 1px solid #ddd;
                padding: 10px;
                text-align: left;
            }}
            th {{
                background-color: #dbeafe;
            }}
            .status {{
                border-left: 8px solid {status_color};
            }}
            .feedback {{
                background-color: #eef6ff;
                padding: 12px;
                margin-top: 10px;
                border-left: 5px solid #1e3a5f;
                border-radius: 6px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Lægeside - Blodtryksdata</h1>

            <div class="card">
                <h2>Vælg patient</h2>
                <form method="GET" action="/doctor">
                    <select name="patient_id" onchange="this.form.submit()">
    """

    for p in patients:
        selected = "selected" if p["id"] == patient["id"] else ""
        html += f"""
                        <option value="{p["id"]}" {selected}>
                            {escape(p["name"])}
                        </option>
        """

    html += f"""
                    </select>
                </form>
            </div>

            <div class="card">
                <h2>Patientinformation</h2>
                <p><strong>Navn:</strong> {escape(patient["name"])}</p>
                <p><strong>Alder:</strong> {patient["age"]}</p>
                <p><strong>Diagnose:</strong> {escape(patient["diagnosis"] or "")}</p>
            </div>

            <div class="card status">
                <h2>Blodtryksstatus</h2>
                <p><strong>Status:</strong> {status}</p>
                <p>{status_text}</p>
                <p><strong>Gennemsnit systolisk:</strong> {avg_systolic}</p>
                <p><strong>Gennemsnit diastolisk:</strong> {avg_diastolic}</p>
            </div>

            <div class="card">
                <h2>Patientens blodtryksmålinger</h2>
                <table>
                    <tr>
                        <th>Dato/tid</th>
                        <th>Systolisk</th>
                        <th>Diastolisk</th>
                        <th>Puls</th>
                    </tr>
    """

    for m in measurements:
        html += f"""
                    <tr>
                        <td>{escape(m["measured_at"])}</td>
                        <td>{m["systolic"]}</td>
                        <td>{m["diastolic"]}</td>
                        <td>{m["pulse"] if m["pulse"] is not None else "-"}</td>
                    </tr>
        """

    html += f"""
                </table>
            </div>

            <div class="card">
                <h2>Giv feedback til patienten</h2>
                <form method="POST" action="/add_feedback">
                    <input type="hidden" name="patient_id" value="{patient["id"]}">

                    <label>Feedback</label>
                    <textarea name="message" rows="5" placeholder="Skriv feedback til patienten..." required></textarea>

                    <button type="submit">Send feedback</button>
                </form>
            </div>

            <div class="card">
                <h2>Tidligere feedback</h2>
    """

    if len(feedback_list) == 0:
        html += "<p>Der er endnu ingen feedback til denne patient.</p>"
    else:
        for f in feedback_list:
            html += f"""
                <div class="feedback">
                    <strong>{escape(f["created_at"])}</strong>
                    <p>{escape(f["message"])}</p>
                </div>
            """

    html += """
            </div>
        </div>
    </body>
    </html>
    """

    return html


@app.route("/add_feedback", methods=["POST"])
def add_feedback_route():
    patient_id = int(request.form["patient_id"])
    message = request.form["message"]

    add_feedback(
        patient_id=patient_id,
        message=message
    )

    return redirect(f"/doctor?patient_id={patient_id}")


@app.route("/save_measurements", methods=["POST"])
def save_measurements():
    data = request.get_json()
    patient_id = data["patient_id"]

    for m in data["measurements"]:
        add_measurement(
            patient_id=patient_id,
            systolic=m["sys"],
            diastolic=m["dia"],
            pulse=m.get("puls")
        )

    return jsonify({"status": "ok"})

@app.route("/patient")
def patient_page():
    with open("patientside.html", "r", encoding="utf-8") as file:
        return file.read()
    
if __name__ == "__main__":
    app.run(debug=True)