# init_db.py
import sqlite3, os

DB_PATH = os.path.join(os.path.dirname(__file__), "dementia_app.db")

def init_db():
    # Remove old DB for clean rebuild
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    # Enable foreign keys
    conn.execute("PRAGMA foreign_keys = ON;")

    # Load and execute schema
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    with open(schema_path, "r", encoding="utf-8") as f:
        conn.executescript(f.read()) # THIS MAKES THE DB

    # Insert demo roles
    conn.execute("INSERT INTO Role (RoleName) VALUES ('carer'), ('family_member');")

    # Insert demo users
    conn.execute("""
        INSERT INTO User (RoleID, FirstName, LastName, Email, PasswordHash)
        VALUES
        (1, 'John', 'Doe', 'john.doe@healthcare.com', 'hashed_password_1'),
        (1, 'Jane', 'Smith', 'jane.smith@healthcare.com', 'hashed_password_2'),
        (2, 'Emily', 'Taylor', 'emily.taylor@gmail.com', 'hashed_password_3');
    """)

    # Insert demo patient
    conn.execute("""
        INSERT INTO Patient (CarerID, FirstName, LastName, ResidenceType, Address, DementiaType, DementiaStage)
        VALUES
        (1, 'William', 'Williamson', 'Home', '123 Grove Street', 'Alzheimers', 'Early');
    """)

    # Link family member to patient
    conn.execute("""
        INSERT INTO Family_Member (UserID, PatientID, PhoneNumber, ContentAccessLvl)
        VALUES
        (3, 1, '07123-456789', 'general');
    """)

    # Add sample log entries
    conn.execute("""
        INSERT INTO Log_Item (PatientID, AuthorID, Content, ContentLvl)
        VALUES
        (1, 1, 'Morning checkup complete, vitals stable.', 'general'),
        (1, 1, 'Administered medication: Donepezil 10mg.', 'private');
    """)

    # Add tasks
    conn.execute("""
        INSERT INTO Task (PatientID, Title, Description, DueDate, Completed)
        VALUES
        (1, 'Check Blood Pressure', 'Morning routine check', datetime('now', '+1 hour'), 0),
        (1, 'Administer Medication', 'Give morning meds', datetime('now', '+2 hour'), 0);
    """)

    # Add medications
    conn.execute("""
        INSERT INTO Medication (PatientID, Name, Dosage, Time, Active)
        VALUES
        (1, 'Donepezil', '10mg', '08:00', 1),
        (1, 'Memantine', '5mg', '20:00', 1);
    """)

    # Add chat message
    conn.execute("""
        INSERT INTO Message (FromUserID, ToUserID, PatientID, Content)
        VALUES
        (1, 3, 1, 'Good morning Emily, William had a great night sleep!');
    """)

    # Add notification
    conn.execute("""
        INSERT INTO Notification (UserID, Type, Message)
        VALUES
        (3, 'update', 'New log entry submitted for William Williamson.');
    """)

    conn.commit()
    conn.close()
    print("Database initialised successfully with demo data.")

if __name__ == "__main__":
    init_db()
