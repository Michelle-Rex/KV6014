import sqlite3
import os
from pathlib import Path
from datetime import date, timedelta

DB_PATH = Path(__file__).parent.parent / "dementia_care.db"

def init_db():
    # remove old database
    if DB_PATH.exists():
        os.remove(DB_PATH)
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    
    # load schema
    schema_path = Path(__file__).parent / "schema.sql"
    with open(schema_path, "r") as f:
        conn.executescript(f.read())
    
    print("Database schema created")
    

    conn.execute("INSERT INTO Role (RoleName) VALUES ('carer'), ('family_member')")
    
    conn.execute("""
        INSERT INTO User (RoleID, FirstName, LastName, Email, PasswordHash)
        VALUES
        (1, 'John', 'Doe', 'john.doe@healthcare.com', 'hashed_password_1'),
        (1, 'Jane', 'Smith', 'jane.smith@healthcare.com', 'hashed_password_2'),
        (2, 'Emily', 'Taylor', 'emily.taylor@gmail.com', 'hashed_password_3')
    """)
    
    conn.execute("""
        INSERT INTO Patient (CarerID, FirstName, LastName, ResidenceType, Address, DementiaType, DementiaStage)
        VALUES
        (1, 'William', 'Williamson', 'Home', '123 Grove Street', 'Alzheimers', 'Early'),
        (1, 'Margaret', 'Brown', 'Care Home', '45 Oak Avenue', 'Vascular', 'Mid'),
        (1, 'Robert', 'Taylor', 'Care Home', '78 Elm Road', 'Mixed', 'Late'),
        (1, 'Dorothy', 'Jones', 'Care Home', '12 Maple Street', 'Alzheimers', 'Early')
    """)
    
    conn.execute("""
        INSERT INTO Family_Member (UserID, PatientID, PhoneNumber, ContentAccessLvl)
        VALUES
        (3, 1, '07123-456789', 'basic')
    """)
    
    conn.execute("""
        INSERT INTO Log_Item (PatientID, AuthorID, Content, ContentLvl)
        VALUES
        (1, 1, 'Morning checkup complete, vitals stable.', 'general'),
        (1, 1, 'Administered medication: Donepezil 10mg.', 'private')
    """)
    
    conn.execute("""
        INSERT INTO Task (PatientID, Title, Description, DueDate, Completed)
        VALUES
        (1, 'Check Blood Pressure', 'Morning routine check', datetime('now', '+1 hour'), 0),
        (1, 'Administer Medication', 'Give morning meds', datetime('now', '+2 hour'), 0),
        (2, 'Morning medication', 'Give meds', datetime('now', '+1 hour'), 1),
        (3, 'Comfort check', 'Check patient comfort', datetime('now', '+30 minutes'), 0),
        (4, 'Morning walk', 'Assisted walk', datetime('now', '+3 hour'), 0)
    """)
    
    conn.execute("""
        INSERT INTO Medication (PatientID, Name, Dosage, Time, Active)
        VALUES
        (1, 'Donepezil', '10mg', '08:00', 1),
        (1, 'Memantine', '5mg', '20:00', 1),
        (2, 'Rivastigmine', '6mg', '08:00', 1),
        (3, 'Galantamine', '8mg', '09:30', 1),
        (4, 'Aricept', '5mg', '08:30', 1)
    """)
    
    conn.execute("""
        INSERT INTO Message (FromUserID, ToUserID, PatientID, Content)
        VALUES
        (1, 3, 1, 'Good morning Emily, William had a great night sleep!')
    """)
    
    conn.execute("""
        INSERT INTO Notification (UserID, Type, Message)
        VALUES
        (3, 'update', 'New log entry submitted for William Williamson.')
    """)
    
    
# ADDITIONAL DEMO DATA
    conn.execute("""
        INSERT INTO PatientDetails (
            PatientNumber, FirstName, LastName, DateOfBirth,
            Gender, RoomNumber, DementiaStage, GPName, GPPhone, GPPractice,
            Allergies, MedicalConditions, Mobility
        ) VALUES
        ('P1', 'William', 'Williamson', '1945-03-15', 'Male', 'A101', 'Early', 'Dr. Johnson', '020 1234 5678', 'City Medical Centre', 'Penicillin', 'Hypertension', 'Walks with aid'),
        ('P2', 'Margaret', 'Brown', '1950-07-22', 'Female', 'A102', 'Mid', 'Dr. Wilson', '020 2345 6789', 'Heath Practice', 'None', 'Arthritis', 'Wheelchair user'),
        ('P3', 'Robert', 'Taylor', '1948-11-30', 'Male', 'B201', 'Late', 'Dr. Davis', '020 3456 7890', 'Park Surgery', 'Latex', 'Heart disease', 'Bedridden'),
        ('P4', 'Dorothy', 'Jones', '1952-02-10', 'Female', 'A103', 'Early', 'Dr. Thompson', '020 4567 8901', 'Green Lane Surgery', 'None', 'None', 'Independent')
    """)
    
    conn.execute("""
        INSERT INTO EmergencyContacts (PatientID, Name, Relationship, Phone, Email, IsPrimary)
        VALUES
        (1, 'Emily Smith', 'Daughter', '07700 900123', 'emily.smith@email.com', 1),
        (1, 'James Smith', 'Son', '07700 900124', 'james.smith@email.com', 0),
        (2, 'Sarah Brown', 'Daughter', '07700 900125', 'sarah.brown@email.com', 1),
        (3, 'Michael Taylor', 'Son', '07700 900126', 'michael.t@email.com', 1),
        (4, 'Peter Jones', 'Husband', '07700 900128', 'peter.jones@email.com', 1)
    """)
    
    conn.execute("""
        INSERT INTO MedicationDetails (MedicationID, Frequency, Route, Prescriber, Purpose)
        VALUES
        (1, 'Once daily', 'Oral', 'Dr. Johnson', 'Memory improvement'),
        (2, 'Once daily', 'Oral', 'Dr. Johnson', 'Alzheimers treatment'),
        (3, 'Twice daily', 'Oral', 'Dr. Wilson', 'Cognitive function'),
        (4, 'Twice daily', 'Oral', 'Dr. Davis', 'Dementia symptoms'),
        (5, 'Once daily', 'Oral', 'Dr. Thompson', 'Early stage treatment')
    """)
    
    conn.execute("""
        INSERT INTO TaskDetails (TaskID, Priority, ScheduledTime, Recurring)
        VALUES
        (1, 'High', '09:00', 1),
        (2, 'High', '10:00', 1),
        (3, 'High', '08:00', 1),
        (4, 'Urgent', '11:00', 1),
        (5, 'Low', '10:30', 1)
    """)
    
    today = date.today().isoformat()
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    
    conn.execute("""
        INSERT INTO DailyLogs (
            PatientID, CarerID, LogDate, LogTime,
            Temperature, BloodPressure, HeartRate, OxygenSaturation, Weight,
            Mood, SleepQuality, Appetite, ActivityLevel, SocialEngagement,
            GeneralNotes
        ) VALUES
        (1, NULL, ?, '10:00', 37.0, '120/80', 75, 98, 70.5, 'Good', 'Fair', 'Good', 'Moderate', 'Good', 'Patient had a good morning'),
        (1, NULL, ?, '10:15', 36.9, '122/78', 74, 98, 70.4, 'Very Good', 'Good', 'Excellent', 'Active', 'Excellent', 'Excellent day'),
        (2, NULL, ?, '09:30', 36.8, '118/78', 72, 99, 65.0, 'Very Good', 'Good', 'Excellent', 'Active', 'Excellent', 'Family visited'),
        (3, NULL, ?, '11:00', 37.2, '125/82', 78, 96, 68.0, 'Neutral', 'Poor', 'Fair', 'Limited', 'Minimal', 'Restless night')
    """, (yesterday, today, today, today))
    
    conn.execute("""
        INSERT INTO Meals (LogID, MealType, AmountConsumed, Calories, FluidsMl)
        VALUES
        (1, 'Breakfast', '75%', 400, 250),
        (1, 'Lunch', '100%', 600, 300),
        (1, 'Dinner', '50%', 450, 200),
        (2, 'Breakfast', '100%', 500, 300),
        (2, 'Lunch', '100%', 650, 350),
        (3, 'Breakfast', '100%', 500, 300),
        (3, 'Lunch', '100%', 700, 400),
        (4, 'Breakfast', '25%', 200, 100)
    """)
    
    
    
    conn.commit()
    conn.close()
    
    print("Database initialised successfully with demo data")

if __name__ == "__main__":
    init_db()