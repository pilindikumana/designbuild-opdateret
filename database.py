from pathlib import Path
import sqlite3

DB_PATH = Path("sqlite.db")

def connect():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    return con

def init_database():
    with connect() as con:
        con.executescript("""
        PRAGMA foreign_keys = ON;

        CREATE TABLE IF NOT EXISTS user (
          id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
          username TEXT NOT NULL UNIQUE,
          password TEXT NOT NULL,
          role TEXT NOT NULL,
          created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS patient (
          id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
          user_id INTEGER REFERENCES user(id) ON DELETE SET NULL,
          name TEXT NOT NULL,
          age INTEGER,
          cpr TEXT,
          phone TEXT,
          diagnosis TEXT,
          created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS blood_pressure_measurement (
          id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
          patient_id INTEGER NOT NULL REFERENCES patient(id) ON DELETE CASCADE,
          measured_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
          systolic INTEGER NOT NULL,
          diastolic INTEGER NOT NULL,
          pulse INTEGER,
          note TEXT,
          created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS feedback (
          id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
          patient_id INTEGER NOT NULL REFERENCES patient(id) ON DELETE CASCADE,
          author_user_id INTEGER REFERENCES user(id) ON DELETE SET NULL,
          message TEXT NOT NULL,
          created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE UNIQUE INDEX IF NOT EXISTS user_username_unique_idx ON user(username);
        CREATE INDEX IF NOT EXISTS patient_user_id_idx ON patient(user_id);
        CREATE INDEX IF NOT EXISTS measurement_patient_id_idx ON blood_pressure_measurement(patient_id);
        CREATE INDEX IF NOT EXISTS feedback_patient_id_idx ON feedback(patient_id);
        """)

def seed_database():
    patients = [
        ("Ali Hassan", 55, "Hypertension", [
            ("2026-06-10T09:00:00", 145, 90, 72),
            ("2026-06-12T09:00:00", 138, 85, 70),
            ("2026-06-15T09:00:00", 142, 88, 74),
        ]),
        ("Sara Jensen", 43, "Kontrolmålinger", [
            ("2026-06-10T09:00:00", 120, 78, 68),
            ("2026-06-12T09:00:00", 118, 76, 66),
            ("2026-06-15T09:00:00", 122, 80, 69),
        ]),
        ("Mads Nielsen", 61, "Hypertension", [
            ("2026-06-10T09:00:00", 160, 96, 80),
            ("2026-06-12T09:00:00", 155, 94, 78),
            ("2026-06-15T09:00:00", 158, 95, 82),
        ]),
    ]

    with connect() as con:
        existing = con.execute("SELECT COUNT(*) FROM patient").fetchone()[0]

        if existing == 0:
            for name, age, diagnosis, measurements in patients:
                cur = con.execute(
                    """
                    INSERT INTO patient (name, age, diagnosis)
                    VALUES (?, ?, ?)
                    """,
                    (name, age, diagnosis)
                )

                patient_id = cur.lastrowid

                for measured_at, systolic, diastolic, pulse in measurements:
                    con.execute(
                        """
                        INSERT INTO blood_pressure_measurement
                        (patient_id, measured_at, systolic, diastolic, pulse)
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (patient_id, measured_at, systolic, diastolic, pulse)
                    )

def add_patient(name, age=None, diagnosis=None, cpr=None, phone=None, user_id=None):
    with connect() as con:
        cur = con.execute(
            """
            INSERT INTO patient (name, age, diagnosis, cpr, phone, user_id)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (name, age, diagnosis, cpr, phone, user_id)
        )
        return cur.lastrowid

def add_measurement(patient_id, systolic, diastolic, pulse=None, note=None, measured_at=None):
    with connect() as con:
        con.execute(
            """
            INSERT INTO blood_pressure_measurement
            (patient_id, measured_at, systolic, diastolic, pulse, note)
            VALUES (?, COALESCE(?, CURRENT_TIMESTAMP), ?, ?, ?, ?)
            """,
            (patient_id, measured_at, systolic, diastolic, pulse, note)
        )

def add_feedback(patient_id, message, author_user_id=None):
    with connect() as con:
        con.execute(
            """
            INSERT INTO feedback (patient_id, author_user_id, message)
            VALUES (?, ?, ?)
            """,
            (patient_id, author_user_id, message)
        )

def get_all_patients():
    with connect() as con:
        return con.execute("""
            SELECT * FROM patient
            ORDER BY id
        """).fetchall()

def get_patient_measurements(patient_id):
    with connect() as con:
        return con.execute("""
            SELECT *
            FROM blood_pressure_measurement
            WHERE patient_id = ?
            ORDER BY measured_at DESC
        """, (patient_id,)).fetchall()

def get_patient_feedback(patient_id):
    with connect() as con:
        return con.execute("""
            SELECT *
            FROM feedback
            WHERE patient_id = ?
            ORDER BY created_at DESC
        """, (patient_id,)).fetchall()

def print_database():
    patients = get_all_patients()

    for patient in patients:
        print(f"\nPatient: {patient['name']} | Alder: {patient['age']} | Diagnose: {patient['diagnosis']}")

        measurements = get_patient_measurements(patient["id"])
        for m in measurements:
            print(f"  BT: {m['systolic']}/{m['diastolic']} | Puls: {m['pulse']} | Tid: {m['measured_at']}")

        feedback = get_patient_feedback(patient["id"])
        for f in feedback:
            print(f"  Feedback: {f['message']}")

if __name__ == "__main__":
    init_database()
    seed_database()
    print_database()
    print(f"\nDatabase klar: {DB_PATH.resolve()}")
