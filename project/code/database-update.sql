-- Add City column to Leads table
-- This script should be run manually if the database already exists

-- Check if the column exists before adding it
IF NOT EXISTS (
    SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_NAME = 'Leads' 
    AND COLUMN_NAME = 'City'
)
BEGIN
    ALTER TABLE Leads ADD City NVARCHAR(100) NULL;
    PRINT 'City column added to Leads table';
END
ELSE
BEGIN
    PRINT 'City column already exists in Leads table';
END

-- Update existing leads with sample city data
UPDATE Leads 
SET City = CASE 
    WHEN City IS NULL THEN 
        CASE ABS(CHECKSUM(NEWID())) % 20
            WHEN 0 THEN 'New York'
            WHEN 1 THEN 'Los Angeles'
            WHEN 2 THEN 'Chicago'
            WHEN 3 THEN 'Houston'
            WHEN 4 THEN 'Phoenix'
            WHEN 5 THEN 'Philadelphia'
            WHEN 6 THEN 'San Antonio'
            WHEN 7 THEN 'San Diego'
            WHEN 8 THEN 'Dallas'
            WHEN 9 THEN 'San Jose'
            WHEN 10 THEN 'Austin'
            WHEN 11 THEN 'Jacksonville'
            WHEN 12 THEN 'Fort Worth'
            WHEN 13 THEN 'Columbus'
            WHEN 14 THEN 'Charlotte'
            WHEN 15 THEN 'San Francisco'
            WHEN 16 THEN 'Indianapolis'
            WHEN 17 THEN 'Seattle'
            WHEN 18 THEN 'Denver'
            ELSE 'Boston'
        END
    ELSE City
END
WHERE City IS NULL;

PRINT 'Updated existing leads with city data';