#!/usr/bin/env python3
import sqlite3
import os
from datetime import datetime

# Database path
db_path = "ByteForge.db"

# Remove existing database
if os.path.exists(db_path):
    os.remove(db_path)
    print(f"Removed existing database: {db_path}")

# Create new database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print(f"Created new database: {db_path}")

# Create AspNetUsers table
cursor.execute('''
CREATE TABLE AspNetUsers (
    Id TEXT PRIMARY KEY,
    UserName TEXT,
    NormalizedUserName TEXT,
    Email TEXT,
    NormalizedEmail TEXT,
    EmailConfirmed INTEGER,
    PasswordHash TEXT,
    SecurityStamp TEXT,
    ConcurrencyStamp TEXT,
    PhoneNumber TEXT,
    PhoneNumberConfirmed INTEGER,
    TwoFactorEnabled INTEGER,
    LockoutEnabled INTEGER,
    LockoutEnd TEXT,
    AccessFailedCount INTEGER
);
''')

# Create AspNetRoles table
cursor.execute('''
CREATE TABLE AspNetRoles (
    Id TEXT PRIMARY KEY,
    Name TEXT,
    NormalizedName TEXT,
    ConcurrencyStamp TEXT
);
''')

# Create Projects table
cursor.execute('''
CREATE TABLE Projects (
    Id TEXT PRIMARY KEY,
    Name TEXT NOT NULL,
    Description TEXT,
    ProjectType TEXT,
    Status TEXT,
    TenantId TEXT,
    CreatedAt TEXT,
    UpdatedAt TEXT,
    CreatedBy TEXT,
    CompletionPercentage INTEGER DEFAULT 0,
    EstimatedHours INTEGER DEFAULT 0,
    ActualHours INTEGER DEFAULT 0
);
''')

# Create WorkflowSettings table
cursor.execute('''
CREATE TABLE WorkflowSettings (
    Id TEXT PRIMARY KEY,
    TenantId TEXT,
    WorkflowType TEXT,
    Configuration TEXT,
    IsActive INTEGER,
    CreatedAt TEXT,
    UpdatedAt TEXT
);
''')

# Create ProjectDocuments table
cursor.execute('''
CREATE TABLE ProjectDocuments (
    Id TEXT PRIMARY KEY,
    ProjectId TEXT,
    DocumentType TEXT,
    Title TEXT,
    Content TEXT,
    Status TEXT,
    Version TEXT,
    CreatedAt TEXT,
    UpdatedAt TEXT,
    CreatedBy TEXT,
    FOREIGN KEY (ProjectId) REFERENCES Projects(Id)
);
''')

# Create RequirementTraceabilityMatrix table
cursor.execute('''
CREATE TABLE RequirementTraceabilityMatrix (
    Id TEXT PRIMARY KEY,
    ProjectId TEXT,
    SourceRequirement TEXT,
    TargetRequirement TEXT,
    LinkType TEXT,
    CreatedAt TEXT,
    FOREIGN KEY (ProjectId) REFERENCES Projects(Id)
);
''')

# Create __EFMigrationsHistory table
cursor.execute('''
CREATE TABLE __EFMigrationsHistory (
    MigrationId TEXT PRIMARY KEY,
    ProductVersion TEXT
);
''')

# Insert initial migration record
cursor.execute('''
INSERT INTO __EFMigrationsHistory (MigrationId, ProductVersion) 
VALUES ('20240724000000_InitialCreate', '8.0.12');
''')

# Insert sample data
sample_user_id = "user-001"
sample_project_id = "project-001"

# Insert sample user
cursor.execute('''
INSERT INTO AspNetUsers (
    Id, UserName, NormalizedUserName, Email, NormalizedEmail, 
    EmailConfirmed, SecurityStamp, ConcurrencyStamp, TwoFactorEnabled, 
    LockoutEnabled, AccessFailedCount
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
''', (
    sample_user_id, "admin@example.com", "ADMIN@EXAMPLE.COM", 
    "admin@example.com", "ADMIN@EXAMPLE.COM", 1, 
    "security-stamp", "concurrency-stamp", 0, 1, 0
))

# Insert sample project
cursor.execute('''
INSERT INTO Projects (
    Id, Name, Description, ProjectType, Status, TenantId, 
    CreatedAt, UpdatedAt, CreatedBy, CompletionPercentage
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
''', (
    sample_project_id, "Sample ByteForge Project", 
    "A sample project for testing the ByteForge system", 
    "CRM", "Active", "tenant-001", 
    datetime.utcnow().isoformat(), datetime.utcnow().isoformat(), 
    sample_user_id, 25
))

# Insert sample workflow settings
cursor.execute('''
INSERT INTO WorkflowSettings (
    Id, TenantId, WorkflowType, Configuration, IsActive, 
    CreatedAt, UpdatedAt
) VALUES (?, ?, ?, ?, ?, ?, ?);
''', (
    "workflow-001", "tenant-001", "DocumentGeneration", 
    '{"maxRetries": 3, "timeout": 300}', 1,
    datetime.utcnow().isoformat(), datetime.utcnow().isoformat()
))

# Insert sample document
cursor.execute('''
INSERT INTO ProjectDocuments (
    Id, ProjectId, DocumentType, Title, Content, Status, 
    Version, CreatedAt, UpdatedAt, CreatedBy
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
''', (
    "doc-001", sample_project_id, "BRD", 
    "Business Requirements Document", 
    "# Business Requirements Document\n\nThis is a sample BRD for testing purposes.", 
    "Completed", "1.0", 
    datetime.utcnow().isoformat(), datetime.utcnow().isoformat(), 
    sample_user_id
))

# Commit changes and close connection
conn.commit()
conn.close()

print("Database setup completed successfully!")
print("Created tables:")
print("- AspNetUsers")
print("- AspNetRoles") 
print("- Projects")
print("- WorkflowSettings")
print("- ProjectDocuments")
print("- RequirementTraceabilityMatrix")
print("- __EFMigrationsHistory")
print("\nInserted sample data:")
print(f"- Sample user: {sample_user_id}")
print(f"- Sample project: {sample_project_id}")
print("- Sample workflow settings")
print("- Sample document")