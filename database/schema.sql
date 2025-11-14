PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS Role (
    RoleID INTEGER PRIMARY KEY AUTOINCREMENT,
    RoleName TEXT NOT NULL CHECK (RoleName IN ('carer', 'family_member'))
);

CREATE TABLE IF NOT EXISTS User (
    UserID INTEGER PRIMARY KEY AUTOINCREMENT,
    RoleID INTEGER NOT NULL,
    FirstName TEXT NOT NULL,
    LastName TEXT NOT NULL,
    Email TEXT NOT NULL UNIQUE,
    PasswordHash TEXT NOT NULL,
    FOREIGN KEY (RoleID) REFERENCES Role(RoleID)
);

CREATE TABLE IF NOT EXISTS Patient (
    PatientID INTEGER PRIMARY KEY AUTOINCREMENT,
    CarerID INTEGER,
    FirstName TEXT NOT NULL,
    LastName TEXT NOT NULL,
    ResidenceType TEXT CHECK (ResidenceType IN ('Home', 'Care Home', 'Hospital', 'Other')) DEFAULT 'Home',
    Address TEXT,
    DementiaType TEXT,
    DementiaStage TEXT CHECK (DementiaStage IN ('Early', 'Mid', 'Late')) DEFAULT 'Early',
    FOREIGN KEY (CarerID) REFERENCES User(UserID)
);

CREATE TABLE IF NOT EXISTS Family_Member (
    FamilyMemberID INTEGER PRIMARY KEY AUTOINCREMENT,
    UserID INTEGER NOT NULL,
    PatientID INTEGER NOT NULL,
    PhoneNumber TEXT,
    ContentAccessLvl TEXT CHECK (ContentAccessLvl IN ('basic', 'detailed', 'full')) DEFAULT 'basic',
    FOREIGN KEY (UserID) REFERENCES User(UserID),
    FOREIGN KEY (PatientID) REFERENCES Patient(PatientID)
);

CREATE TABLE IF NOT EXISTS Log_Item (
    LogID INTEGER PRIMARY KEY AUTOINCREMENT,
    PatientID INTEGER NOT NULL,
    AuthorID INTEGER NOT NULL,
    Content TEXT NOT NULL,
    ContentLvl TEXT CHECK (ContentLvl IN ('censored', 'general', 'private')) DEFAULT 'general',
    DateTime DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (PatientID) REFERENCES Patient(PatientID),
    FOREIGN KEY (AuthorID) REFERENCES User(UserID)
);

CREATE TABLE IF NOT EXISTS Task (
    TaskID INTEGER PRIMARY KEY AUTOINCREMENT,
    PatientID INTEGER NOT NULL,
    Title TEXT NOT NULL,
    Description TEXT,
    DueDate DATETIME,
    Completed INTEGER DEFAULT 0,
    FOREIGN KEY (PatientID) REFERENCES Patient(PatientID)
);

CREATE TABLE IF NOT EXISTS Medication (
    MedicationID INTEGER PRIMARY KEY AUTOINCREMENT,
    PatientID INTEGER NOT NULL,
    Name TEXT NOT NULL,
    Dosage TEXT,
    Time TEXT,
    Active INTEGER DEFAULT 1,
    FOREIGN KEY (PatientID) REFERENCES Patient(PatientID)
);

CREATE TABLE IF NOT EXISTS Message (
    MessageID INTEGER PRIMARY KEY AUTOINCREMENT,
    FromUserID INTEGER NOT NULL,
    ToUserID INTEGER NOT NULL,
    PatientID INTEGER NOT NULL,
    Content TEXT,
    ImagePath TEXT,
    Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (FromUserID) REFERENCES User(UserID),
    FOREIGN KEY (ToUserID) REFERENCES User(UserID),
    FOREIGN KEY (PatientID) REFERENCES Patient(PatientID)
);

CREATE TABLE IF NOT EXISTS Notification (
    NotificationID INTEGER PRIMARY KEY AUTOINCREMENT,
    UserID INTEGER NOT NULL,
    Type TEXT,
    Message TEXT,
    CreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
    ReadFlag INTEGER DEFAULT 0,
    FOREIGN KEY (UserID) REFERENCES User(UserID)
);

-- ADDITIONAL TABLES 

CREATE TABLE IF NOT EXISTS PatientDetails (
    DetailID INTEGER PRIMARY KEY AUTOINCREMENT,
    PatientNumber TEXT UNIQUE NOT NULL,
    FirstName TEXT NOT NULL,
    LastName TEXT NOT NULL,
    DateOfBirth DATE,
    Gender TEXT,
    RoomNumber TEXT,
    DementiaStage TEXT CHECK (DementiaStage IN ('Early', 'Mid', 'Late', '')),
    DementiaType TEXT,
    ResidenceType TEXT CHECK (ResidenceType IN ('Home', 'Care Home', 'Hospital', 'Other')) DEFAULT 'Care Home',
    Address TEXT,
    GPName TEXT,
    GPPhone TEXT,
    GPPractice TEXT,
    Allergies TEXT,
    MedicalConditions TEXT,
    Mobility TEXT CHECK (Mobility IN ('Independent', 'Walks with aid', 'Wheelchair user', 'Bedridden', '')),
    DietaryRequirements TEXT,
    CareNotes TEXT,
    CreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS EmergencyContacts (
    ContactID INTEGER PRIMARY KEY AUTOINCREMENT,
    PatientID INTEGER NOT NULL,
    Name TEXT NOT NULL,
    Relationship TEXT NOT NULL,
    Phone TEXT NOT NULL,
    Email TEXT,
    IsPrimary INTEGER DEFAULT 0 CHECK (IsPrimary IN (0, 1)),
    FOREIGN KEY (PatientID) REFERENCES Patient(PatientID) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS DailyLogs (
    LogID INTEGER PRIMARY KEY AUTOINCREMENT,
    PatientID INTEGER NOT NULL,
    CarerID INTEGER,
    LogDate DATE NOT NULL,
    LogTime TIME,
    Temperature REAL CHECK (Temperature BETWEEN 35.0 AND 42.0),
    BloodPressure TEXT,
    HeartRate INTEGER CHECK (HeartRate BETWEEN 40 AND 200),
    OxygenSaturation INTEGER CHECK (OxygenSaturation BETWEEN 70 AND 100),
    Weight REAL CHECK (Weight > 0),
    Mood TEXT,
    SleepQuality TEXT,
    Appetite TEXT,
    ActivityLevel TEXT,
    SocialEngagement TEXT,
    GeneralNotes TEXT,
    Incidents TEXT,
    CreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (PatientID) REFERENCES Patient(PatientID) ON DELETE CASCADE,
    FOREIGN KEY (CarerID) REFERENCES User(UserID)
);

CREATE TABLE IF NOT EXISTS Meals (
    MealID INTEGER PRIMARY KEY AUTOINCREMENT,
    LogID INTEGER NOT NULL,
    MealType TEXT CHECK (MealType IN ('Breakfast', 'Lunch', 'Dinner')),
    AmountConsumed TEXT CHECK (AmountConsumed IN ('None', '25%', '50%', '75%', '100%')),
    Calories INTEGER CHECK (Calories >= 0),
    FluidsMl INTEGER CHECK (FluidsMl >= 0),
    FOREIGN KEY (LogID) REFERENCES DailyLogs(LogID) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS MedicationDetails (
    MedDetailID INTEGER PRIMARY KEY AUTOINCREMENT,
    MedicationID INTEGER NOT NULL UNIQUE,
    Frequency TEXT,
    Route TEXT,
    Prescriber TEXT,
    Purpose TEXT,
    StartDate DATE,
    EndDate DATE,
    FOREIGN KEY (MedicationID) REFERENCES Medication(MedicationID) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS TaskDetails (
    TaskDetailID INTEGER PRIMARY KEY AUTOINCREMENT,
    TaskID INTEGER NOT NULL UNIQUE,
    Priority TEXT CHECK (Priority IN ('Low', 'Medium', 'High', 'Urgent')) DEFAULT 'Medium',
    ScheduledTime TIME,
    Notes TEXT,
    Recurring INTEGER DEFAULT 0 CHECK (Recurring IN (0, 1)),
    CompletedAt DATETIME,
    CompletedBy INTEGER,
    FOREIGN KEY (TaskID) REFERENCES Task(TaskID) ON DELETE CASCADE,
    FOREIGN KEY (CompletedBy) REFERENCES User(UserID)
);

CREATE TABLE IF NOT EXISTS MemoryBook (
    MemoryID INTEGER PRIMARY KEY AUTOINCREMENT,
    PatientID INTEGER NOT NULL,
    UploadedBy INTEGER,
    Title TEXT NOT NULL,
    MediaType TEXT CHECK (MediaType IN ('Photo', 'Video', 'Audio')),
    Category TEXT,
    Description TEXT,
    PeopleTagged TEXT,
    FileName TEXT,
    FileType TEXT,
    FileData BLOB,
    UploadedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (PatientID) REFERENCES Patient(PatientID) ON DELETE CASCADE,
    FOREIGN KEY (UploadedBy) REFERENCES User(UserID)
);

INSERT OR IGNORE INTO Role (RoleName) VALUES ('carer'), ('family_member');