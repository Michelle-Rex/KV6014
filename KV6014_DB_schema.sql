BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "Family_Member" (
	"FamilyMemberID"	INTEGER NOT NULL,
	"UserID"	INTEGER NOT NULL,
	"PatientID"	INTEGER NOT NULL,
	"PhoneNumber"	TEXT NOT NULL,
	"ContentAccessLvl"	TEXT NOT NULL DEFAULT 'basic',
	PRIMARY KEY("FamilyMemberID" AUTOINCREMENT),
	FOREIGN KEY("PatientID") REFERENCES "Patient"("PatientID"),
	FOREIGN KEY("UserID") REFERENCES "User"("UserID"),
	CHECK("ContentAccessLvl" IN ('basic', 'detailed', 'full'))
);
CREATE TABLE IF NOT EXISTS "Log_Item" (
	"LogID"	INTEGER,
	"PatientID"	INTEGER NOT NULL,
	"AuthorID"	INTEGER NOT NULL,
	"Content"	TEXT NOT NULL,
	"ContentLvl"	TEXT NOT NULL DEFAULT 'basic',
	"DateTime"	DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY("LogID" AUTOINCREMENT),
	FOREIGN KEY("AuthorID") REFERENCES "User"("UserID"),
	FOREIGN KEY("PatientID") REFERENCES "Patient"("PatientID"),
	CHECK("ContentLvl" IN ('basic', 'detailed', 'full'))
);
CREATE TABLE IF NOT EXISTS "Patient" (
	"PatientID"	INTEGER,
	"CarerID"	INTEGER NOT NULL,
	"FirstName"	TEXT NOT NULL,
	"LastName"	TEXT NOT NULL,
	"ResidenceType"	TEXT NOT NULL DEFAULT 'home',
	"Address"	TEXT NOT NULL,
	"DementiaType"	TEXT NOT NULL,
	"DementiaStage"	TEXT NOT NULL DEFAULT '''early',
	PRIMARY KEY("PatientID" AUTOINCREMENT),
	FOREIGN KEY("CarerID") REFERENCES "User"("UserID"),
	CHECK("ResidenceType" IN ('home', 'care home', 'hospital', 'other')),
	CHECK("DementiaStage" IN ('aarly', 'mid', 'late'))
);
CREATE TABLE IF NOT EXISTS "Role" (
	"RoleID"	INTEGER NOT NULL,
	"RoleName"	TEXT NOT NULL,
	PRIMARY KEY("RoleID" AUTOINCREMENT),
	CHECK("RoleName" IN ('carer', 'family'))
);
CREATE TABLE IF NOT EXISTS "User" (
	"UserID"	INTEGER NOT NULL,
	"RoleID"	INTEGER NOT NULL,
	"FirstName"	TEXT NOT NULL,
	"LastName"	TEXT NOT NULL,
	"Email"	TEXT NOT NULL,
	"PasswordHash"	TEXT NOT NULL,
	PRIMARY KEY("UserID" AUTOINCREMENT),
	FOREIGN KEY("RoleID") REFERENCES ""
);
COMMIT;
