import sqlite3

conn = sqlite3.connect("KV6014_DB.db")
cur = conn.cursor()

def add_to_task(task: object):
    #pretty sure there's a better way to do this with json, but this will do for now
    title = task.getTaskName()
    desc = task.getTaskDesc()
    due_date = task.getDueDate()
    cur.execute(f"INSERT INTO Task (Title, Description, DueDate) VALUES ({title}, {desc}, {due_date})")
    conn.commit()
    print("task created and added to list")


def delete_from_task(taskID: int):
    cur.execute(f"DELETE FROM Task WHERE TaskID = {taskID}")
    conn.commit()
    print("task deleted")

def view_patient_tasks(patientID: int):
    for row in cur.execute(f'SELECT Title, Description, DueDate, Completed FROM Task WHERE PatientID = {patientID}'):
        print(row) #need to make this a proper output


def edit_task(taskID: int):
    pass