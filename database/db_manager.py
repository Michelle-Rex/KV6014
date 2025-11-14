import sqlite3
import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, date

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_name="dementia_care.db"):
        self.db_path = Path(db_name)
        self.schema_path = Path(__file__).parent / "schema.sql"
        logger.info(f"Initialising database at {self.db_path}")
        self.init_db()
    
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    
    def init_db(self):
        try:
            if not self.schema_path.exists():
                raise FileNotFoundError(f"Schema file not found at {self.schema_path}")
            
            with open(self.schema_path, 'r') as f:
                schema_sql = f.read()
            
            conn = self.get_connection()
            conn.executescript(schema_sql)
            conn.close()
            
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    def add_patient_details(self, patient_id: int, details: Dict) -> bool:
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO PatientDetails (
                    PatientNumber, FirstName, LastName, DateOfBirth,
                    Gender, RoomNumber, DementiaStage, DementiaType,
                    ResidenceType, Address, GPName, GPPhone, GPPractice,
                    Allergies, MedicalConditions, Mobility, DietaryRequirements, CareNotes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                details['patient_number'],
                details['first_name'],
                details['last_name'],
                details.get('date_of_birth', ''),
                details.get('gender', ''),
                details.get('room_number', ''),
                details.get('dementia_stage', ''),
                details.get('dementia_type', ''),
                details.get('residence_type', 'Care Home'),
                details.get('address', ''),
                details.get('gp_name', ''),
                details.get('gp_phone', ''),
                details.get('gp_practice', ''),
                details.get('allergies', ''),
                details.get('medical_conditions', ''),
                details.get('mobility', ''),
                details.get('dietary_requirements', ''),
                details.get('care_notes', '')
            ))
            
            for contact in details.get('emergency_contacts', []):
                cursor.execute('''
                    INSERT INTO EmergencyContacts (PatientID, Name, Relationship, Phone, Email)
                    VALUES (?, ?, ?, ?, ?)
                ''', (patient_id, contact['name'], contact['relationship'], contact['phone'], contact.get('email', '')))
            
            conn.commit()
            logger.info(f"Patient details added for patient {patient_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding patient details: {e}", exc_info=True)
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                conn.close()
    
    def get_patient_details(self, patient_id: int) -> Optional[Dict]:
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM PatientDetails WHERE DetailID = ?', (patient_id,))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            cursor.execute('SELECT * FROM EmergencyContacts WHERE PatientID = ?', (patient_id,))
            contacts = cursor.fetchall()
            
            emergency_contacts = [
                {
                    'contact_id': c['ContactID'],
                    'name': c['Name'],
                    'relationship': c['Relationship'],
                    'phone': c['Phone'],
                    'email': c['Email']
                }
                for c in contacts
            ]
            
            return {
                'detail_id': row['DetailID'],
                'patient_number': row['PatientNumber'],
                'first_name': row['FirstName'],
                'last_name': row['LastName'],
                'date_of_birth': row['DateOfBirth'],
                'gender': row['Gender'],
                'room_number': row['RoomNumber'],
                'dementia_stage': row['DementiaStage'],
                'dementia_type': row['DementiaType'],
                'residence_type': row['ResidenceType'],
                'address': row['Address'],
                'gp_name': row['GPName'],
                'gp_phone': row['GPPhone'],
                'gp_practice': row['GPPractice'],
                'allergies': row['Allergies'],
                'medical_conditions': row['MedicalConditions'],
                'mobility': row['Mobility'],
                'dietary_requirements': row['DietaryRequirements'],
                'care_notes': row['CareNotes'],
                'created_at': row['CreatedAt'],
                'emergency_contacts': emergency_contacts
            }
            
        except Exception as e:
            logger.error(f"Error getting patient details: {e}", exc_info=True)
            return None
        finally:
            if conn:
                conn.close()
    
    def get_all_patient_details(self) -> List[Dict]:
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM PatientDetails')
            rows = cursor.fetchall()
            
            patients = []
            for row in rows:
                detail_id = row['DetailID']
                
                cursor.execute('SELECT * FROM EmergencyContacts WHERE PatientID = ?', (detail_id,))
                contacts = cursor.fetchall()
                
                emergency_contacts = [
                    {
                        'contact_id': c['ContactID'],
                        'name': c['Name'],
                        'relationship': c['Relationship'],
                        'phone': c['Phone'],
                        'email': c['Email']
                    }
                    for c in contacts
                ]
                
                patients.append({
                    'patient_id': detail_id,
                    'patient_number': row['PatientNumber'],
                    'first_name': row['FirstName'],
                    'last_name': row['LastName'],
                    'date_of_birth': row['DateOfBirth'],
                    'gender': row['Gender'],
                    'room_number': row['RoomNumber'],
                    'dementia_stage': row['DementiaStage'],
                    'gp_name': row['GPName'],
                    'gp_phone': row['GPPhone'],
                    'gp_practice': row['GPPractice'],
                    'allergies': row['Allergies'],
                    'medical_conditions': row['MedicalConditions'],
                    'mobility': row['Mobility'],
                    'dietary_requirements': row['DietaryRequirements'],
                    'care_notes': row['CareNotes'],
                    'created_at': row['CreatedAt'],
                    'emergency_contacts': emergency_contacts
                })
            
            return patients
            
        except Exception as e:
            logger.error(f"Error getting all patient details: {e}", exc_info=True)
            return []
        finally:
            if conn:
                conn.close()
    
    def search_patient_details(self, search_term: str) -> List[Dict]:
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            search_pattern = f"%{search_term}%"
            cursor.execute('''
                SELECT * FROM PatientDetails
                WHERE PatientNumber LIKE ? 
                   OR FirstName LIKE ? 
                   OR LastName LIKE ?
                   OR RoomNumber LIKE ?
            ''', (search_pattern, search_pattern, search_pattern, search_pattern))
            
            rows = cursor.fetchall()
            
            patients = []
            for row in rows:
                detail_id = row['DetailID']
                
                cursor.execute('SELECT * FROM EmergencyContacts WHERE PatientID = ?', (detail_id,))
                contacts = cursor.fetchall()
                
                emergency_contacts = [
                    {'name': c['Name'], 'relationship': c['Relationship'], 'phone': c['Phone']}
                    for c in contacts
                ]
                
                patients.append({
                    'patient_id': detail_id,
                    'patient_number': row['PatientNumber'],
                    'first_name': row['FirstName'],
                    'last_name': row['LastName'],
                    'room_number': row['RoomNumber'],
                    'dementia_stage': row['DementiaStage'],
                    'emergency_contacts': emergency_contacts
                })
            
            return patients
            
        except Exception as e:
            logger.error(f"Error searching patients: {e}", exc_info=True)
            return []
        finally:
            if conn:
                conn.close()
    
    def filter_patients_by_stage(self, stage: str) -> List[Dict]:
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM PatientDetails WHERE DementiaStage = ?', (stage,))
            rows = cursor.fetchall()
            
            patients = []
            for row in rows:
                patients.append({
                    'patient_id': row['DetailID'],
                    'patient_number': row['PatientNumber'],
                    'first_name': row['FirstName'],
                    'last_name': row['LastName'],
                    'dementia_stage': row['DementiaStage']
                })
            
            return patients
            
        except Exception as e:
            logger.error(f"Error filtering patients: {e}", exc_info=True)
            return []
        finally:
            if conn:
                conn.close()
    
    def add_daily_log(self, log_data: Dict) -> Optional[int]:
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO DailyLogs (
                    PatientID, CarerID, LogDate, LogTime,
                    Temperature, BloodPressure, HeartRate, OxygenSaturation, Weight,
                    Mood, SleepQuality, Appetite, ActivityLevel,
                    SocialEngagement, GeneralNotes, Incidents
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                log_data['patient_id'],
                log_data.get('carer_id'),
                log_data['log_date'],
                log_data.get('log_time', ''),
                log_data['temperature'],
                log_data['blood_pressure'],
                log_data['heart_rate'],
                log_data['oxygen_saturation'],
                log_data['weight'],
                log_data['mood'],
                log_data['sleep_quality'],
                log_data['appetite'],
                log_data['activity_level'],
                log_data['social_engagement'],
                log_data.get('general_notes', ''),
                log_data.get('incidents', '')
            ))
            
            log_id = cursor.lastrowid
            
            for meal_type, meal_data in log_data.get('meals', {}).items():
                if meal_type in ['Breakfast', 'Lunch', 'Dinner']:
                    cursor.execute('''
                        INSERT INTO Meals (LogID, MealType, AmountConsumed, Calories, FluidsMl)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (
                        log_id,
                        meal_type,
                        meal_data.get('amount', 'None'),
                        meal_data.get('calories', 0),
                        0
                    ))
            
            conn.commit()
            logger.info(f"Daily log added for patient {log_data['patient_id']}")
            return log_id
            
        except Exception as e:
            logger.error(f"Error adding daily log: {e}", exc_info=True)
            if conn:
                conn.rollback()
            return None
        finally:
            if conn:
                conn.close()
    
    def get_patient_logs(self, patient_id: int, start_date: str = None, end_date: str = None) -> List[Dict]:
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            if start_date and end_date:
                cursor.execute('''
                    SELECT * FROM DailyLogs 
                    WHERE PatientID = ? AND LogDate BETWEEN ? AND ?
                    ORDER BY LogDate DESC, LogTime DESC
                ''', (patient_id, start_date, end_date))
            else:
                cursor.execute('''
                    SELECT * FROM DailyLogs 
                    WHERE PatientID = ?
                    ORDER BY LogDate DESC, LogTime DESC
                ''', (patient_id,))
            
            log_rows = cursor.fetchall()
            
            logs = []
            for row in log_rows:
                log_id = row['LogID']
                
                cursor.execute('SELECT * FROM Meals WHERE LogID = ?', (log_id,))
                meal_rows = cursor.fetchall()
                
                meals = {}
                total_calories = 0
                for meal in meal_rows:
                    meal_type = meal['MealType'].lower()
                    meals[meal_type] = {
                        'amount': meal['AmountConsumed'],
                        'calories': meal['Calories']
                    }
                    total_calories += meal['Calories'] if meal['Calories'] else 0
                
                logs.append({
                    'log_id': row['LogID'],
                    'patient_id': row['PatientID'],
                    'date': row['LogDate'],
                    'time': row['LogTime'],
                    'vitals': {
                        'temperature': row['Temperature'],
                        'blood_pressure': row['BloodPressure'],
                        'heart_rate': row['HeartRate'],
                        'oxygen_saturation': row['OxygenSaturation'],
                        'weight': row['Weight']
                    },
                    'activities': {
                        'mood': row['Mood'],
                        'sleep_quality': row['SleepQuality'],
                        'appetite': row['Appetite'],
                        'activity_level': row['ActivityLevel'],
                        'social_engagement': row['SocialEngagement']
                    },
                    'meals': meals,
                    'total_calories': total_calories,
                    'general_notes': row['GeneralNotes'],
                    'incidents': row['Incidents'],
                    'created_at': row['CreatedAt']
                })
            
            return logs
            
        except Exception as e:
            logger.error(f"Error getting logs: {e}", exc_info=True)
            return []
        finally:
            if conn:
                conn.close()
    
    def add_medication_details(self, med_id: int, details: Dict) -> bool:
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO MedicationDetails (
                    MedicationID, Frequency, Route, Prescriber, Purpose, StartDate, EndDate
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                med_id,
                details.get('frequency', ''),
                details.get('route', ''),
                details.get('prescriber', ''),
                details.get('purpose', ''),
                details.get('start_date', ''),
                details.get('end_date', '')
            ))
            
            conn.commit()
            logger.info(f"Medication details added for medication {med_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding medication details: {e}", exc_info=True)
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                conn.close()
    
    def get_medication_details(self, med_id: int) -> Optional[Dict]:
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM MedicationDetails WHERE MedicationID = ?', (med_id,))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            return {
                'medication_id': row['MedicationID'],
                'frequency': row['Frequency'],
                'route': row['Route'],
                'prescriber': row['Prescriber'],
                'purpose': row['Purpose'],
                'start_date': row['StartDate'],
                'end_date': row['EndDate']
            }
            
        except Exception as e:
            logger.error(f"Error getting medication details: {e}", exc_info=True)
            return None
        finally:
            if conn:
                conn.close()
    
    def add_task_details(self, task_id: int, details: Dict) -> bool:
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO TaskDetails (
                    TaskID, Priority, ScheduledTime, Notes, Recurring
                ) VALUES (?, ?, ?, ?, ?)
            ''', (
                task_id,
                details.get('priority', 'Medium'),
                details.get('scheduled_time', ''),
                details.get('notes', ''),
                details.get('recurring', 0)
            ))
            
            conn.commit()
            logger.info(f"Task details added for task {task_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding task details: {e}", exc_info=True)
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                conn.close()
    
    def update_task_completion(self, task_id: int, completed: bool, completed_by: int = None) -> bool:
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            if completed:
                cursor.execute(
                    'UPDATE TaskDetails SET CompletedAt = ?, CompletedBy = ? WHERE TaskID = ?',
                    (datetime.now().isoformat(), completed_by, task_id)
                )
            else:
                cursor.execute(
                    'UPDATE TaskDetails SET CompletedAt = ?, CompletedBy = ? WHERE TaskID = ?',
                    (None, None, task_id)
                )
            
            conn.commit()
            logger.info(f"Task {task_id} completion updated")
            return True
            
        except Exception as e:
            logger.error(f"Error updating task: {e}", exc_info=True)
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                conn.close()
    
    def add_memory(self, memory_data: Dict) -> Optional[int]:
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO MemoryBook (
                    PatientID, UploadedBy, Title, MediaType,
                    Category, Description, PeopleTagged,
                    FileName, FileType, FileData
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                memory_data['patient_id'],
                memory_data.get('uploaded_by'),
                memory_data['title'],
                memory_data['media_type'],
                memory_data.get('category', ''),
                memory_data.get('description', ''),
                memory_data.get('people_tagged', ''),
                memory_data.get('file_name', ''),
                memory_data.get('file_type', ''),
                memory_data.get('file_data', b'')
            ))
            
            memory_id = cursor.lastrowid
            conn.commit()
            logger.info(f"Memory added with ID {memory_id}")
            return memory_id
            
        except Exception as e:
            logger.error(f"Error adding memory: {e}", exc_info=True)
            if conn:
                conn.rollback()
            return None
        finally:
            if conn:
                conn.close()
    
    def get_patient_memories(self, patient_id: int, category: str = None) -> List[Dict]:
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            if category and category != "All":
                cursor.execute(
                    'SELECT * FROM MemoryBook WHERE PatientID = ? AND Category = ? ORDER BY UploadedAt DESC',
                    (patient_id, category)
                )
            else:
                cursor.execute(
                    'SELECT * FROM MemoryBook WHERE PatientID = ? ORDER BY UploadedAt DESC',
                    (patient_id,)
                )
            
            rows = cursor.fetchall()
            
            memories = []
            for row in rows:
                memories.append({
                    'memory_id': row['MemoryID'],
                    'patient_id': row['PatientID'],
                    'title': row['Title'],
                    'media_type': row['MediaType'],
                    'category': row['Category'],
                    'description': row['Description'],
                    'people_tagged': row['PeopleTagged'],
                    'file_name': row['FileName'],
                    'file_type': row['FileType'],
                    'file_data': row['FileData'],
                    'uploaded_at': row['UploadedAt']
                })
            
            return memories
            
        except Exception as e:
            logger.error(f"Error getting memories: {e}", exc_info=True)
            return []
        finally:
            if conn:
                conn.close()
    
    def delete_memory(self, memory_id: int) -> bool:
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM MemoryBook WHERE MemoryID = ?', (memory_id,))
            conn.commit()
            logger.info(f"Memory {memory_id} deleted")
            return True
        except Exception as e:
            logger.error(f"Error deleting memory: {e}", exc_info=True)
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                conn.close()

    def get_all_patients(self) -> List[Dict]:
        return self.get_all_patient_details()
    
    def get_dashboard_stats(self) -> Dict:
        conn = self.get_connection()
        cursor = conn.cursor()
        
        total_patients = cursor.execute("SELECT COUNT(*) FROM Patient").fetchone()[0]
        pending_tasks = cursor.execute("SELECT COUNT(*) FROM Task WHERE Completed = 0").fetchone()[0]
        active_medications = cursor.execute("SELECT COUNT(*) FROM Medication WHERE Active = 1").fetchone()[0]
        logs_today = cursor.execute("SELECT COUNT(*) FROM DailyLogs WHERE LogDate = ?", (date.today().isoformat(),)).fetchone()[0]
        
        conn.close()
        return {
            'total_patients': total_patients,
            'pending_tasks': pending_tasks,
            'active_medications': active_medications,
            'logs_today': logs_today
        }
    
    def get_patient_tasks(self, patient_id: int) -> List[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT t.TaskID, t.Title as task_name, t.Description, t.DueDate, t.Completed,
                   td.Priority, td.ScheduledTime, td.Notes, td.Recurring, 
                   td.CompletedAt, td.CompletedBy
            FROM Task t
            LEFT JOIN TaskDetails td ON td.TaskID = t.TaskID
            WHERE t.PatientID = ?
            ORDER BY t.Completed, td.Priority, td.ScheduledTime
        """, (patient_id,))
        
        tasks = []
        for row in cursor.fetchall():
            tasks.append({
                'task_id': row['TaskID'],
                'task_name': row['task_name'],
                'description': row['Description'],
                'due_date': row['DueDate'],
                'completed': bool(row['Completed']),
                'priority': row['Priority'] or 'Medium',
                'scheduled_time': row['ScheduledTime'],
                'notes': row['Notes'],
                'recurring': bool(row['Recurring']),
                'completed_at': row['CompletedAt'],
                'completed_by': row['CompletedBy']
            })
        
        conn.close()
        return tasks
    
    def add_task(self, task_data: Dict) -> Optional[int]:
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("INSERT INTO Task (PatientID, Title, Description, DueDate, Completed) VALUES (?, ?, ?, ?, 0)",
            (task_data['patient_id'], task_data['task_name'], task_data.get('description', ''), task_data.get('due_date')))
        
        task_id = cursor.lastrowid
        
        cursor.execute("INSERT INTO TaskDetails (TaskID, Priority, ScheduledTime, Notes, Recurring) VALUES (?, ?, ?, ?, ?)",
            (task_id, task_data.get('priority', 'Medium'), task_data.get('scheduled_time', ''), 
             task_data.get('notes', ''), task_data.get('recurring', 0)))
        
        conn.commit()
        conn.close()
        return task_id
    
    def delete_task(self, task_id: int) -> bool:
        conn = self.get_connection()
        conn.execute("DELETE FROM Task WHERE TaskID = ?", (task_id,))
        conn.commit()
        conn.close()
        return True
    
    def get_patient_medications(self, patient_id: int, active_only: bool = True) -> List[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT m.MedicationID, m.Name, m.Dosage, m.Time as scheduled_time, m.Active,
                   md.Frequency, md.Route, md.Prescriber, md.Purpose, md.StartDate, md.EndDate
            FROM Medication m
            LEFT JOIN MedicationDetails md ON md.MedicationID = m.MedicationID
            WHERE m.PatientID = ?
        """
        
        if active_only:
            query += " AND m.Active = 1"
        query += " ORDER BY m.Time"
        
        cursor.execute(query, (patient_id,))
        
        meds = []
        for row in cursor.fetchall():
            meds.append({
                'medication_id': row['MedicationID'],
                'name': row['Name'],
                'dosage': row['Dosage'],
                'scheduled_time': row['scheduled_time'],
                'active': bool(row['Active']),
                'frequency': row['Frequency'],
                'route': row['Route'],
                'prescriber': row['Prescriber'],
                'purpose': row['Purpose'],
                'start_date': row['StartDate'],
                'end_date': row['EndDate']
            })
        
        conn.close()
        return meds
    
    def add_medication(self, med_data: Dict) -> Optional[int]:
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("INSERT INTO Medication (PatientID, Name, Dosage, Time, Active) VALUES (?, ?, ?, ?, 1)",
            (med_data['patient_id'], med_data['name'], med_data['dosage'], med_data['scheduled_time']))
        
        med_id = cursor.lastrowid
        
        cursor.execute("INSERT INTO MedicationDetails (MedicationID, Frequency, Route, Prescriber, Purpose) VALUES (?, ?, ?, ?, ?)",
            (med_id, med_data.get('frequency', ''), med_data.get('route', ''), 
             med_data.get('prescriber', ''), med_data.get('purpose', '')))
        
        conn.commit()
        conn.close()
        return med_id
    
    def update_medication_status(self, med_id: int, active: bool) -> bool:
        conn = self.get_connection()
        conn.execute("UPDATE Medication SET Active = ? WHERE MedicationID = ?", (1 if active else 0, med_id))
        conn.commit()
        conn.close()
        return True
    
    def get_family_patients(self, user_id: int) -> List[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT p.PatientID, p.FirstName, p.LastName, 
                   pd.PatientNumber, pd.RoomNumber, pd.DementiaStage
            FROM Family_Member fm
            JOIN Patient p ON p.PatientID = fm.PatientID
            LEFT JOIN PatientDetails pd ON pd.DetailID = p.PatientID
            WHERE fm.UserID = ?
        """, (user_id,))
        
        patients = []
        for row in cursor.fetchall():
            patients.append({
                'patient_id': row['PatientID'],
                'first_name': row['FirstName'],
                'last_name': row['LastName'],
                'patient_number': row['PatientNumber'] or f"P{row['PatientID']}",
                'room_number': row['RoomNumber'],
                'dementia_stage': row['DementiaStage']
            })
        
        conn.close()
        return patients


if __name__ == "__main__":
    db = Database()
    print(f"Database created at: {db.db_path.absolute()}")
    print("Schema loaded")