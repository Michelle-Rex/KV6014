# test_db.py
import sqlite3, os

#DB_PATH = os.path.join(os.path.dirname(__file__), "dementia_app.db")
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "dementia_care.db")

def test_db():
    assert os.path.exists(DB_PATH), "Database file not found. Did you run init_db.py?"

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    print("Connected to database:", DB_PATH)
    print("====================================")

    # List of all tables to inspect
    tables = [
        "Role",
        "User",
        "Patient",
        "Family_Member",
        "Log_Item",
        "Task",
        "Medication",
        "Message",
        "Notification"
    ]

    for table in tables:
        print(f"\n=== {table} ===")
        rows = cursor.execute(f"SELECT * FROM {table}").fetchall()
        if rows:
            for row in rows:
                print(" | ".join(f"{k}: {row[k]}" for k in row.keys()))
        else:
            print("(empty)")
        print("------------------------------------")

    print("\nRunning Integrity Assertions...")

    # 1. Roles
    roles = cursor.execute("SELECT RoleName FROM Role").fetchall()
    role_names = [r["RoleName"] for r in roles]
    assert "carer" in role_names and "family_member" in role_names, "Roles missing expected entries"

    # 2. Users exist
    user_count = cursor.execute("SELECT COUNT(*) FROM User").fetchone()[0]
    assert user_count >= 2, "Expected at least two users (carer + family)"

    # 3. Patients exist
    patient_count = cursor.execute("SELECT COUNT(*) FROM Patient").fetchone()[0]
    assert patient_count >= 1, "Expected at least one patient"

    # 4. Carer relationship valid
    result = cursor.execute("""
        SELECT COUNT(*) 
        FROM Patient p 
        JOIN User u ON u.UserID = p.CarerID 
        WHERE u.RoleID = (SELECT RoleID FROM Role WHERE RoleName = 'carer')
    """).fetchone()[0]
    assert result >= 1, "No valid carer assigned to patient"

    # 5. Family linked correctly
    fam_links = cursor.execute("""
        SELECT COUNT(*) 
        FROM Family_Member f 
        JOIN Patient p ON p.PatientID = f.PatientID 
        JOIN User u ON u.UserID = f.UserID
    """).fetchone()[0]
    assert fam_links >= 1, "No valid family-member link found"

    # 6. Logs, Tasks, and Medications linked to a valid patient
    for table in ["Log_Item", "Task", "Medication"]:
        q = f"SELECT COUNT(*) FROM {table} WHERE PatientID IN (SELECT PatientID FROM Patient)"
        count = cursor.execute(q).fetchone()[0]
        assert count >= 1, f"Table {table} has no linked data."

    # 7. Message linkage check
    msg_check = cursor.execute("""
        SELECT COUNT(*) FROM Message 
        WHERE FromUserID IN (SELECT UserID FROM User)
        AND ToUserID IN (SELECT UserID FROM User)
    """).fetchone()[0]
    assert msg_check >= 1, "No valid message linkage"

    # 8. Notifications assigned to users
    notif_check = cursor.execute("""
        SELECT COUNT(*) FROM Notification
        WHERE UserID IN (SELECT UserID FROM User)
    """).fetchone()[0]
    assert notif_check >= 1, "No valid notification entries"

    print("All integrity checks passed successfully!")

    conn.close()
    print("\nDatabase test completed.\n")

if __name__ == "__main__":
    test_db()