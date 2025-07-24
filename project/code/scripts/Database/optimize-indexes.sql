-- ByteForgeFrontend Database Optimization Script
-- This script creates optimal indexes for performance based on common query patterns

-- Projects table indexes
CREATE INDEX IF NOT EXISTS IX_Projects_TenantId_Status 
ON Projects(TenantId, Status) 
INCLUDE (Name, CreatedAt, CurrentPhase);

CREATE INDEX IF NOT EXISTS IX_Projects_CreatedBy_CreatedAt 
ON Projects(CreatedBy, CreatedAt DESC);

CREATE INDEX IF NOT EXISTS IX_Projects_CurrentPhase 
ON Projects(CurrentPhase) 
WHERE Status = 'Active';

-- ProjectDocuments table indexes
CREATE INDEX IF NOT EXISTS IX_ProjectDocuments_ProjectId_Type 
ON ProjectDocuments(ProjectId, Type) 
INCLUDE (Version, CreatedAt);

CREATE INDEX IF NOT EXISTS IX_ProjectDocuments_Type_CreatedAt 
ON ProjectDocuments(Type, CreatedAt DESC);

-- Create unique index for document versions
CREATE UNIQUE INDEX IF NOT EXISTS UX_ProjectDocuments_ProjectId_Type_Version 
ON ProjectDocuments(ProjectId, Type, Version);

-- AuditLogs table indexes (critical for compliance and security)
CREATE INDEX IF NOT EXISTS IX_AuditLogs_TenantId_Timestamp 
ON AuditLogs(TenantId, Timestamp DESC) 
INCLUDE (Action, UserId, EntityId);

CREATE INDEX IF NOT EXISTS IX_AuditLogs_UserId_Timestamp 
ON AuditLogs(UserId, Timestamp DESC);

CREATE INDEX IF NOT EXISTS IX_AuditLogs_EntityId_EntityType 
ON AuditLogs(EntityId, EntityType) 
WHERE EntityId IS NOT NULL;

CREATE INDEX IF NOT EXISTS IX_AuditLogs_Action_Category 
ON AuditLogs(Action, Category) 
INCLUDE (Timestamp, TenantId);

-- ApiKeys table indexes
CREATE INDEX IF NOT EXISTS IX_ApiKeys_UserId_IsActive 
ON ApiKeys(UserId, IsActive) 
WHERE IsActive = 1;

CREATE INDEX IF NOT EXISTS IX_ApiKeys_HashedKey 
ON ApiKeys(HashedKey) 
WHERE IsActive = 1;

CREATE INDEX IF NOT EXISTS IX_ApiKeys_ExpiresAt 
ON ApiKeys(ExpiresAt) 
WHERE IsActive = 1 AND ExpiresAt IS NOT NULL;

-- Templates table indexes
CREATE INDEX IF NOT EXISTS IX_ProjectTemplates_TenantId_Category 
ON ProjectTemplates(TenantId, Category) 
WHERE IsActive = 1;

CREATE INDEX IF NOT EXISTS IX_ProjectTemplates_IsPublic_Category 
ON ProjectTemplates(IsPublic, Category) 
WHERE IsActive = 1;

-- Users table indexes (for multi-tenancy)
CREATE INDEX IF NOT EXISTS IX_AspNetUsers_TenantId 
ON AspNetUsers(TenantId) 
INCLUDE (Email, UserName);

-- Monitoring data indexes (if stored in database)
CREATE INDEX IF NOT EXISTS IX_MonitoringEvents_ProjectId_Timestamp 
ON MonitoringEvents(ProjectId, Timestamp DESC) 
WHERE EXISTS;

CREATE INDEX IF NOT EXISTS IX_MonitoringEvents_EventType_Timestamp 
ON MonitoringEvents(EventType, Timestamp DESC) 
WHERE EXISTS;

-- Full-text search indexes for document content
CREATE FULLTEXT INDEX IF NOT EXISTS FTX_ProjectDocuments_Content 
ON ProjectDocuments(Content) 
WITH STOPLIST = SYSTEM;

CREATE FULLTEXT INDEX IF NOT EXISTS FTX_Projects_Name_Description 
ON Projects(Name, Description) 
WITH STOPLIST = SYSTEM;

-- Performance tracking indexes
CREATE INDEX IF NOT EXISTS IX_PerformanceMetrics_Operation_Timestamp 
ON PerformanceMetrics(Operation, Timestamp DESC) 
WHERE EXISTS;

-- Composite indexes for complex queries
CREATE INDEX IF NOT EXISTS IX_Projects_Search 
ON Projects(TenantId, Status, Name) 
INCLUDE (Description, CreatedAt, UpdatedAt);

-- Index for requirements traceability queries
CREATE INDEX IF NOT EXISTS IX_RequirementLinks_SourceId_TargetId 
ON RequirementLinks(SourceDocumentId, TargetDocumentId) 
WHERE EXISTS;

-- Statistics update (run periodically)
UPDATE STATISTICS Projects WITH FULLSCAN;
UPDATE STATISTICS ProjectDocuments WITH FULLSCAN;
UPDATE STATISTICS AuditLogs WITH FULLSCAN;
UPDATE STATISTICS ApiKeys WITH FULLSCAN;

-- Query to check index usage and identify missing indexes
SELECT 
    OBJECT_NAME(s.object_id) AS TableName,
    i.name AS IndexName,
    i.type_desc AS IndexType,
    s.user_seeks + s.user_scans + s.user_lookups AS TotalReads,
    s.user_updates AS TotalWrites,
    s.last_user_seek AS LastSeek,
    s.last_user_scan AS LastScan,
    s.last_user_lookup AS LastLookup,
    s.last_user_update AS LastUpdate
FROM sys.dm_db_index_usage_stats s
INNER JOIN sys.indexes i ON s.object_id = i.object_id AND s.index_id = i.index_id
WHERE s.database_id = DB_ID()
ORDER BY TotalReads DESC;

-- Query to find missing indexes
SELECT 
    CONVERT(VARCHAR(30), GETDATE(), 126) AS runtime,
    mig.index_group_handle,
    mid.index_handle,
    CONVERT(DECIMAL(28,1), migs.avg_total_user_cost * migs.avg_user_impact * (migs.user_seeks + migs.user_scans)) AS improvement_measure,
    'CREATE INDEX missing_index_' + CONVERT(VARCHAR, mig.index_group_handle) + '_' + CONVERT(VARCHAR, mid.index_handle) 
    + ' ON ' + mid.statement 
    + ' (' + ISNULL(mid.equality_columns,'') 
    + CASE WHEN mid.equality_columns IS NOT NULL AND mid.inequality_columns IS NOT NULL THEN ',' ELSE '' END 
    + ISNULL(mid.inequality_columns, '')
    + ')' 
    + ISNULL(' INCLUDE (' + mid.included_columns + ')', '') AS create_index_statement,
    migs.*, 
    mid.database_id, 
    mid.[object_id]
FROM sys.dm_db_missing_index_groups mig
INNER JOIN sys.dm_db_missing_index_group_stats migs ON migs.group_handle = mig.index_group_handle
INNER JOIN sys.dm_db_missing_index_details mid ON mig.index_handle = mid.index_handle
WHERE CONVERT(DECIMAL(28,1), migs.avg_total_user_cost * migs.avg_user_impact * (migs.user_seeks + migs.user_scans)) > 10
ORDER BY improvement_measure DESC;