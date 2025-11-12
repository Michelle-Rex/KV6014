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
