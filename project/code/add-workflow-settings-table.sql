-- Add WorkflowSettings table for configuring parallel process counts
-- This script should be run manually to apply the migration
-- Equivalent to EF Core migration: 20250721173800_AddWorkflowSettings

PRINT 'Starting WorkflowSettings table migration...';

-- Check if the table exists before creating it
IF NOT EXISTS (
    SELECT 1 FROM INFORMATION_SCHEMA.TABLES 
    WHERE TABLE_NAME = 'WorkflowSettings'
)
BEGIN
    PRINT 'Creating WorkflowSettings table...';
    
    CREATE TABLE [WorkflowSettings] (
        [Id] int IDENTITY(1,1) NOT NULL,
        [EnrichmentProcessCount] int NOT NULL DEFAULT 10,
        [VettingProcessCount] int NOT NULL DEFAULT 10,
        [ScoringProcessCount] int NOT NULL DEFAULT 10,
        [CrmUpdateProcessCount] int NOT NULL DEFAULT 10,
        [CreatedDate] datetime2 NOT NULL DEFAULT (GETUTCDATE()),
        [ModifiedDate] datetime2 NOT NULL DEFAULT (GETUTCDATE()),
        [ModifiedBy] nvarchar(255) NULL,
        [Notes] nvarchar(500) NULL,
        CONSTRAINT [PK_WorkflowSettings] PRIMARY KEY ([Id])
    );
    
    PRINT 'WorkflowSettings table created successfully';
    
    -- Insert default workflow settings record
    INSERT INTO [WorkflowSettings] 
    ([EnrichmentProcessCount], [VettingProcessCount], [ScoringProcessCount], [CrmUpdateProcessCount], [CreatedDate], [ModifiedDate])
    VALUES (10, 10, 10, 10, GETUTCDATE(), GETUTCDATE());
    
    PRINT 'Default workflow settings inserted (all process counts set to 10)';
    
    -- Update __EFMigrationsHistory table to reflect this migration
    IF EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = '__EFMigrationsHistory')
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM [__EFMigrationsHistory] WHERE [MigrationId] = '20250721173800_AddWorkflowSettings')
        BEGIN
            INSERT INTO [__EFMigrationsHistory] ([MigrationId], [ProductVersion])
            VALUES ('20250721173800_AddWorkflowSettings', '8.0.12');
            PRINT 'Migration history updated';
        END
    END
END
ELSE
BEGIN
    PRINT 'WorkflowSettings table already exists - skipping creation';
END

-- Add constraints to ensure valid ranges (1-100)
IF NOT EXISTS (
    SELECT 1 FROM INFORMATION_SCHEMA.CHECK_CONSTRAINTS 
    WHERE CONSTRAINT_NAME = 'CK_WorkflowSettings_EnrichmentProcessCount'
)
BEGIN
    ALTER TABLE [WorkflowSettings] 
    ADD CONSTRAINT [CK_WorkflowSettings_EnrichmentProcessCount] 
    CHECK ([EnrichmentProcessCount] >= 1 AND [EnrichmentProcessCount] <= 100);
    
    ALTER TABLE [WorkflowSettings] 
    ADD CONSTRAINT [CK_WorkflowSettings_VettingProcessCount] 
    CHECK ([VettingProcessCount] >= 1 AND [VettingProcessCount] <= 100);
    
    ALTER TABLE [WorkflowSettings] 
    ADD CONSTRAINT [CK_WorkflowSettings_ScoringProcessCount] 
    CHECK ([ScoringProcessCount] >= 1 AND [ScoringProcessCount] <= 100);
    
    ALTER TABLE [WorkflowSettings] 
    ADD CONSTRAINT [CK_WorkflowSettings_CrmUpdateProcessCount] 
    CHECK ([CrmUpdateProcessCount] >= 1 AND [CrmUpdateProcessCount] <= 100);
    
    PRINT 'Check constraints added to ensure valid process count ranges (1-100)';
END
ELSE
BEGIN
    PRINT 'Check constraints already exist for WorkflowSettings table';
END

PRINT 'WorkflowSettings table setup complete!';