import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "dementia_care.db")

def test_my_tables():
    assert os.path.exists(DB_PATH), "Database not found. Run: python database/init_db.py"
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print(" DB testing")

    print("=================================")

    print("\nTable Existence Checks ")
    # check tables exist
    my_tables = ['PatientDetails', 'EmergencyContacts', 'DailyLogs', 'Meals', 'MedicationDetails', 'TaskDetails', 'MemoryBook']
    
    for table in my_tables:
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
        assert cursor.fetchone() is not None
        print(f" {table} table exists")


    print("\n Data Integrity Checks ")
    print("=================================")
    
    # check data integrity
    pd_count = cursor.execute("SELECT COUNT(*) FROM PatientDetails").fetchone()[0]
    assert pd_count >= 1
    print(f" PatientDetails has {pd_count} records")
    
    ec_count = cursor.execute("SELECT COUNT(*) FROM EmergencyContacts WHERE PatientID IN (SELECT PatientID FROM Patient)").fetchone()[0]
    assert ec_count >= 1
    print(f" EmergencyContacts has {ec_count} records")
    
    log_count = cursor.execute("SELECT COUNT(*) FROM DailyLogs WHERE PatientID IN (SELECT PatientID FROM Patient)").fetchone()[0]
    assert log_count >= 1
    print(f" DailyLogs has {log_count} records")
    
    meal_count = cursor.execute("SELECT COUNT(*) FROM Meals WHERE LogID IN (SELECT LogID FROM DailyLogs)").fetchone()[0]
    assert meal_count >= 1
    print(f" Meals has {meal_count} records")
    
    med_count = cursor.execute("SELECT COUNT(*) FROM MedicationDetails WHERE MedicationID IN (SELECT MedicationID FROM Medication)").fetchone()[0]
    assert med_count >= 1
    print(f" MedicationDetails has {med_count} records")
    
    task_count = cursor.execute("SELECT COUNT(*) FROM TaskDetails WHERE TaskID IN (SELECT TaskID FROM Task)").fetchone()[0]
    assert task_count >= 1
    print(f" TaskDetails has {task_count} records")
    
    
    conn.close()

if __name__ == "__main__":
    test_my_tables()