import sqlite3

conn = sqlite3.connect("KV6014_DB.db")
cur = conn.cursor()

def add_to_task(task: object):
    #pretty sure there's a better way to do this with json, but this will do for now
    title = task.getTaskName()
    desc = task.getTaskDesc()
    due_date = task.getDueDate()
    cur.execute(f"INSERT INTO Task (Title, Description, DueDate) VALUES ({title}, {desc}, {due_date})")


def delete_from_task():
    pass

def view_patient_tasks():
    #need to get current session's patient ID 
    #patientId = currentPatient.getPatientID()
    data = cur.execute(f'SELECT Title, Description, DueDate, Completed FROM Task WHERE PatientID =')