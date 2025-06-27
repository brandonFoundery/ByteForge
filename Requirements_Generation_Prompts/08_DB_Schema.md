# Database Schema Document (DB-SCHEMA) - Prompt Template

## Primary Prompt

```markdown
You are an expert Database Architect and SQL Developer with extensive experience designing and implementing enterprise database schemas. You excel at translating data requirements into optimized, scalable database structures that support both transactional and analytical workloads.

## Your Task

Generate a complete Database Schema Document for [PROJECT NAME] based on the provided Data Requirements Document (DRD) and technical architecture decisions.

## Input Context Required

1. **Architecture Document**: [Complete Architecture Document with foundational architecture and technology stack]
2. **Data Requirements Document**: [Complete DRD with logical data model]
3. **Technical Requirements Document**: [TRD with database technology choices]
4. **Functional Requirements Document**: [FRD for data access patterns]
5. **Non-Functional Requirements**: [Performance, scalability targets]
6. **Technology Stack**: [Azure SQL Database with Entity Framework Core 8.0+]
7. **Existing Database Standards**: [Naming conventions, patterns if any]

## Document Structure Requirements

Your DB-SCHEMA must include the following sections with YAML frontmatter:

```yaml
---
id: DB-SCHEMA
title: Database Schema Document - [PROJECT NAME]
version: 1.0
status: Draft
created_by: [Your Name]
created_on: YYYY-MM-DD
last_updated: YYYY-MM-DD
upstream: [DRD, TRD, FRD]
downstream: [API-OPEN, Migration Scripts, ORM Mappings]
tags: [database-schema, sql, data-modeling, ddl]
---
```

### 1. Schema Overview

#### 1.1 Database Information
```yaml
database_info:
  dbms: Azure SQL Database
  service_tier: General Purpose
  compute_tier: Provisioned
  name: midway_logistics
  collation: SQL_Latin1_General_CP1_CI_AS
  timezone: UTC
  orm: Entity Framework Core 8.0+
  size_estimate: 250GB initial, 1TB in 3 years
  backup_retention: 35 days
  encryption: Transparent Data Encryption (TDE) enabled
```

#### 1.2 Schema Organization
```yaml
schemas:
  - name: dbo
    description: Default schema for core application tables (Entity Framework Core default)

  - name: Identity
    description: ASP.NET Core Identity tables for authentication

  - name: Logistics
    description: Core logistics business domain tables

  - name: Payments
    description: Payment processing domain tables

  - name: Audit
    description: Audit trail and history tables

  - name: Analytics
    description: Denormalized tables for reporting and analytics

entity_framework_configuration:
  - code_first: true
  - migrations: Entity Framework Core Migrations
  - conventions: Data Annotations and Fluent API
  - connection_pooling: enabled
  - lazy_loading: disabled (explicit loading preferred)
```

#### 1.3 Naming Conventions
```yaml
conventions:
  tables:
    pattern: PascalCase, plural (Entity Framework Core convention)
    example: CustomerOrders

  columns:
    pattern: PascalCase, singular
    example: OrderDate

  primary_keys:
    pattern: Id (Entity Framework Core convention)
    example: Id

  foreign_keys:
    pattern: FK_{child_table}_{parent_table}_{column}
    example: FK_Orders_Customers_CustomerId

  indexes:
    pattern: IX_{table}_{column(s)}
    example: IX_Orders_CreatedDate

  constraints:
    pattern: CK_{table}_{description}
    example: CK_Orders_StatusValid

entity_framework_conventions:
  - Primary keys: Id or {EntityName}Id
  - Foreign keys: {NavigationProperty}Id
  - Navigation properties: PascalCase
  - Collections: Plural PascalCase
  - Value objects: Owned entities
  - Enums: PascalCase with explicit values
```

### 2. Table Definitions

For each table, provide complete DDL:

#### 2.1 Core Business Tables

```sql
-- =============================================
-- Table: Customers
-- Description: Customer master data
-- Schema: dbo
-- Source: DRD-ENTITY-001
-- Entity Framework: Customer entity
-- =============================================

CREATE TABLE [dbo].[Customers] (
    -- Primary Key (Entity Framework Core convention)
    [Id] UNIQUEIDENTIFIER NOT NULL DEFAULT NEWID() PRIMARY KEY,

    -- Business Attributes
    [CustomerNumber] NVARCHAR(20) NOT NULL,
    [CompanyName] NVARCHAR(255) NOT NULL,
    [LegalName] NVARCHAR(255) NULL,
    [TaxId] NVARCHAR(50) NULL,

    -- Contact Information
    [PrimaryEmail] NVARCHAR(255) NOT NULL,
    [SecondaryEmail] NVARCHAR(255) NULL,
    [PrimaryPhone] NVARCHAR(20) NOT NULL,
    [SecondaryPhone] NVARCHAR(20) NULL,

    -- Address Information (Value Object in EF Core)
    [BillingAddressLine1] NVARCHAR(255) NOT NULL,
    [BillingAddressLine2] NVARCHAR(255) NULL,
    [BillingCity] NVARCHAR(100) NOT NULL,
    [BillingState] NVARCHAR(50) NOT NULL,
    [BillingPostalCode] NVARCHAR(20) NOT NULL,
    [BillingCountry] NVARCHAR(2) NOT NULL DEFAULT 'US',

    -- Business Attributes
    [CustomerType] INT NOT NULL, -- Enum: 0=Standard, 1=Premium, 2=VIP
    [CreditLimit] DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    [PaymentTermsDays] INT NOT NULL DEFAULT 30,
    [Status] INT NOT NULL DEFAULT 0, -- Enum: 0=Active, 1=Inactive, 2=Suspended, 3=Closed

    -- Audit Fields (Entity Framework Core conventions)
    [CreatedBy] NVARCHAR(255) NOT NULL,
    [CreatedAt] DATETIME2(7) NOT NULL DEFAULT GETUTCDATE(),
    [UpdatedBy] NVARCHAR(255) NULL,
    [UpdatedAt] DATETIME2(7) NULL,
    [DeletedBy] NVARCHAR(255) NULL,
    [DeletedAt] DATETIME2(7) NULL,
    [RowVersion] ROWVERSION NOT NULL, -- Optimistic concurrency

    -- Constraints
    CONSTRAINT [CK_Customers_CreditLimit] CHECK ([CreditLimit] >= 0),
    CONSTRAINT [CK_Customers_PaymentTerms] CHECK ([PaymentTermsDays] >= 0 AND [PaymentTermsDays] <= 365),
    CONSTRAINT [UQ_Customers_CustomerNumber] UNIQUE ([CustomerNumber]),
    CONSTRAINT [UQ_Customers_PrimaryEmail] UNIQUE ([PrimaryEmail])
);

-- Indexes for performance (Entity Framework Core can generate these)
CREATE NONCLUSTERED INDEX [IX_Customers_CompanyName] ON [dbo].[Customers]([CompanyName]);
CREATE NONCLUSTERED INDEX [IX_Customers_Status] ON [dbo].[Customers]([Status]) WHERE [DeletedAt] IS NULL;
CREATE NONCLUSTERED INDEX [IX_Customers_CreatedAt] ON [dbo].[Customers]([CreatedAt]);

-- Filtered index for active customers
CREATE NONCLUSTERED INDEX [IX_Customers_Active] ON [dbo].[Customers]([Id])
WHERE [Status] = 0 AND [DeletedAt] IS NULL;

-- Extended properties (SQL Server equivalent of comments)
EXEC sp_addextendedproperty
    @name = N'MS_Description', @value = N'Customer master data table',
    @level0type = N'SCHEMA', @level0name = N'dbo',
    @level1type = N'TABLE', @level1name = N'Customers';

EXEC sp_addextendedproperty
    @name = N'MS_Description', @value = N'Unique identifier for customer',
    @level0type = N'SCHEMA', @level0name = N'dbo',
    @level1type = N'TABLE', @level1name = N'Customers',
    @level2type = N'COLUMN', @level2name = N'Id';
```

```sql
-- =============================================
-- Table: orders
-- Description: Customer orders
-- Schema: logistics
-- Source: DRD-ENTITY-002
-- =============================================

CREATE TABLE logistics.orders (
    -- Primary Key
    order_id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    
    -- Foreign Keys
    customer_id UUID NOT NULL REFERENCES public.customers(customer_id),
    carrier_id UUID REFERENCES public.carriers(carrier_id),
    
    -- Business Identifiers
    order_number VARCHAR(50) UNIQUE NOT NULL,
    external_reference VARCHAR(100),
    
    -- Order Details
    order_type VARCHAR(20) NOT NULL CHECK (order_type IN ('STANDARD', 'EXPRESS', 'FREIGHT', 'LTL', 'FTL')),
    order_date TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    requested_pickup_date DATE NOT NULL,
    requested_delivery_date DATE NOT NULL,
    
    -- Status Tracking
    status VARCHAR(30) NOT NULL DEFAULT 'DRAFT' 
        CHECK (status IN ('DRAFT', 'SUBMITTED', 'CONFIRMED', 'IN_TRANSIT', 'DELIVERED', 'CANCELLED', 'FAILED')),
    status_updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Locations (normalized to addresses table)
    pickup_address_id UUID NOT NULL REFERENCES public.addresses(address_id),
    delivery_address_id UUID NOT NULL REFERENCES public.addresses(address_id),
    
    -- Financial
    estimated_amount DECIMAL(15,2),
    actual_amount DECIMAL(15,2),
    currency_code VARCHAR(3) NOT NULL DEFAULT 'USD',
    
    -- Additional Information
    special_instructions TEXT,
    priority INTEGER DEFAULT 5 CHECK (priority BETWEEN 1 AND 10),
    
    -- JSON for flexible attributes
    metadata JSONB,
    
    -- Audit fields
    created_by VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_by VARCHAR(255),
    updated_at TIMESTAMP WITH TIME ZONE,
    version INTEGER NOT NULL DEFAULT 1,
    
    -- Constraints
    CONSTRAINT chk_orders_dates CHECK (requested_delivery_date >= requested_pickup_date),
    CONSTRAINT chk_orders_amounts CHECK (
        (estimated_amount IS NULL OR estimated_amount >= 0) AND
        (actual_amount IS NULL OR actual_amount >= 0)
    )
);

-- Indexes
CREATE INDEX idx_orders_customer_id ON logistics.orders(customer_id);
CREATE INDEX idx_orders_carrier_id ON logistics.orders(carrier_id);
CREATE INDEX idx_orders_order_date ON logistics.orders(order_date DESC);
CREATE INDEX idx_orders_status ON logistics.orders(status);
CREATE INDEX idx_orders_pickup_date ON logistics.orders(requested_pickup_date);

-- Composite indexes for common queries
CREATE INDEX idx_orders_customer_status ON logistics.orders(customer_id, status);
CREATE INDEX idx_orders_date_range ON logistics.orders(order_date, requested_pickup_date, requested_delivery_date);

-- Partial index for active orders
CREATE INDEX idx_orders_active ON logistics.orders(order_id, customer_id, status) 
WHERE status NOT IN ('DELIVERED', 'CANCELLED', 'FAILED');
```

### 3. Relationship Tables

```sql
-- =============================================
-- Table: order_items
-- Description: Line items for orders
-- Schema: logistics
-- Source: DRD-ENTITY-003
-- =============================================

CREATE TABLE logistics.order_items (
    -- Primary Key
    order_item_id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    
    -- Foreign Keys
    order_id UUID NOT NULL REFERENCES logistics.orders(order_id) ON DELETE CASCADE,
    product_id UUID REFERENCES public.products(product_id),
    
    -- Item Details
    line_number INTEGER NOT NULL,
    description VARCHAR(500) NOT NULL,
    quantity DECIMAL(15,4) NOT NULL CHECK (quantity > 0),
    unit_of_measure VARCHAR(10) NOT NULL,
    weight DECIMAL(15,4),
    weight_unit VARCHAR(10) DEFAULT 'LBS',
    
    -- Dimensions
    length DECIMAL(10,2),
    width DECIMAL(10,2),
    height DECIMAL(10,2),
    dimension_unit VARCHAR(10) DEFAULT 'IN',
    
    -- Classification
    freight_class VARCHAR(10),
    hazmat BOOLEAN DEFAULT FALSE,
    
    -- Financial
    unit_price DECIMAL(15,4),
    total_price DECIMAL(15,2),
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE,
    
    -- Constraints
    CONSTRAINT chk_order_items_line_unique UNIQUE (order_id, line_number),
    CONSTRAINT chk_order_items_dimensions CHECK (
        (length IS NULL AND width IS NULL AND height IS NULL) OR
        (length > 0 AND width > 0 AND height > 0)
    )
);

-- Indexes
CREATE INDEX idx_order_items_order_id ON logistics.order_items(order_id);
CREATE INDEX idx_order_items_product_id ON logistics.order_items(product_id);
```

### 4. Audit and History Tables

```sql
-- =============================================
-- Table: audit_log
-- Description: Generic audit trail
-- Schema: audit
-- =============================================

CREATE TABLE audit.audit_log (
    audit_id BIGSERIAL PRIMARY KEY,
    
    -- What was changed
    table_name VARCHAR(100) NOT NULL,
    record_id VARCHAR(100) NOT NULL,
    operation VARCHAR(20) NOT NULL CHECK (operation IN ('INSERT', 'UPDATE', 'DELETE', 'SELECT')),
    
    -- Who made the change
    user_id VARCHAR(255) NOT NULL,
    user_ip INET,
    user_agent TEXT,
    
    -- When it was changed
    occurred_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- What changed (for updates)
    old_values JSONB,
    new_values JSONB,
    changed_fields TEXT[],
    
    -- Additional context
    application_name VARCHAR(100),
    application_version VARCHAR(50),
    correlation_id UUID,
    
    -- Performance optimization
    created_date DATE GENERATED ALWAYS AS (occurred_at::DATE) STORED
) PARTITION BY RANGE (created_date);

-- Create partitions for current and next month
CREATE TABLE audit.audit_log_2025_06 PARTITION OF audit.audit_log
    FOR VALUES FROM ('2025-06-01') TO ('2025-07-01');

-- Indexes
CREATE INDEX idx_audit_log_table_record ON audit.audit_log(table_name, record_id);
CREATE INDEX idx_audit_log_user_id ON audit.audit_log(user_id);
CREATE INDEX idx_audit_log_occurred_at ON audit.audit_log(occurred_at DESC);
```

### 5. Views and Materialized Views

```sql
-- =============================================
-- View: active_customers_summary
-- Description: Summary of active customers with order stats
-- =============================================

CREATE OR REPLACE VIEW public.active_customers_summary AS
SELECT 
    c.customer_id,
    c.customer_number,
    c.company_name,
    c.credit_limit,
    c.payment_terms_days,
    COUNT(DISTINCT o.order_id) AS total_orders,
    COUNT(DISTINCT CASE WHEN o.status = 'DELIVERED' THEN o.order_id END) AS completed_orders,
    COUNT(DISTINCT CASE WHEN o.status IN ('SUBMITTED', 'CONFIRMED', 'IN_TRANSIT') THEN o.order_id END) AS active_orders,
    SUM(o.actual_amount) AS total_revenue,
    MAX(o.order_date) AS last_order_date,
    AVG(o.actual_amount) AS avg_order_value
FROM public.customers c
LEFT JOIN logistics.orders o ON c.customer_id = o.customer_id
WHERE c.status = 'ACTIVE' 
    AND c.deleted_at IS NULL
GROUP BY c.customer_id;

-- Create index on base tables to support this view
CREATE INDEX idx_orders_customer_summary ON logistics.orders(customer_id, status, actual_amount);

COMMENT ON VIEW public.active_customers_summary IS 'Real-time summary of active customers with order statistics';
```

```sql
-- =============================================
-- Materialized View: daily_order_analytics
-- Description: Pre-aggregated order analytics by day
-- =============================================

CREATE MATERIALIZED VIEW analytics.daily_order_analytics AS
SELECT 
    DATE(order_date) AS order_day,
    order_type,
    status,
    COUNT(*) AS order_count,
    SUM(actual_amount) AS total_amount,
    AVG(actual_amount) AS avg_amount,
    MIN(actual_amount) AS min_amount,
    MAX(actual_amount) AS max_amount,
    COUNT(DISTINCT customer_id) AS unique_customers,
    COUNT(DISTINCT carrier_id) AS unique_carriers
FROM logistics.orders
WHERE order_date >= CURRENT_DATE - INTERVAL '90 days'
GROUP BY DATE(order_date), order_type, status
WITH DATA;

-- Indexes on materialized view
CREATE INDEX idx_daily_analytics_date ON analytics.daily_order_analytics(order_day DESC);
CREATE INDEX idx_daily_analytics_type_status ON analytics.daily_order_analytics(order_type, status);

-- Refresh strategy
CREATE OR REPLACE FUNCTION analytics.refresh_daily_order_analytics()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY analytics.daily_order_analytics;
END;
$$ LANGUAGE plpgsql;

-- Schedule refresh (requires pg_cron extension)
-- SELECT cron.schedule('refresh-daily-analytics', '0 1 * * *', 'SELECT analytics.refresh_daily_order_analytics()');
```

### 6. Functions and Procedures

```sql
-- =============================================
-- Function: calculate_order_total
-- Description: Calculate order total with business rules
-- =============================================

CREATE OR REPLACE FUNCTION logistics.calculate_order_total(p_order_id UUID)
RETURNS TABLE (
    subtotal DECIMAL(15,2),
    tax_amount DECIMAL(15,2),
    discount_amount DECIMAL(15,2),
    total_amount DECIMAL(15,2)
) AS $$
DECLARE
    v_subtotal DECIMAL(15,2);
    v_tax_rate DECIMAL(5,4);
    v_discount_rate DECIMAL(5,4);
BEGIN
    -- Calculate subtotal from order items
    SELECT COALESCE(SUM(total_price), 0)
    INTO v_subtotal
    FROM logistics.order_items
    WHERE order_id = p_order_id;
    
    -- Get tax rate (simplified - would be more complex in reality)
    v_tax_rate := 0.0875; -- 8.75%
    
    -- Get customer discount rate
    SELECT CASE 
        WHEN c.customer_type = 'VIP' THEN 0.10
        WHEN c.customer_type = 'PREMIUM' THEN 0.05
        ELSE 0.00
    END
    INTO v_discount_rate
    FROM logistics.orders o
    JOIN public.customers c ON o.customer_id = c.customer_id
    WHERE o.order_id = p_order_id;
    
    -- Return calculated values
    RETURN QUERY
    SELECT 
        v_subtotal,
        v_subtotal * v_tax_rate,
        v_subtotal * v_discount_rate,
        v_subtotal * (1 + v_tax_rate - v_discount_rate);
END;
$$ LANGUAGE plpgsql;

-- Grant execute permission
GRANT EXECUTE ON FUNCTION logistics.calculate_order_total(UUID) TO app_user;
```

```sql
-- =============================================
-- Procedure: archive_old_orders
-- Description: Archive orders older than retention period
-- =============================================

CREATE OR REPLACE PROCEDURE logistics.archive_old_orders(
    p_days_to_keep INTEGER DEFAULT 730
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_archived_count INTEGER;
    v_cutoff_date DATE;
BEGIN
    -- Calculate cutoff date
    v_cutoff_date := CURRENT_DATE - p_days_to_keep;
    
    -- Begin transaction
    BEGIN
        -- Insert into archive tables
        INSERT INTO logistics.orders_archive
        SELECT * FROM logistics.orders
        WHERE order_date < v_cutoff_date
        AND status IN ('DELIVERED', 'CANCELLED');
        
        GET DIAGNOSTICS v_archived_count = ROW_COUNT;
        
        -- Archive related data
        INSERT INTO logistics.order_items_archive
        SELECT oi.* 
        FROM logistics.order_items oi
        JOIN logistics.orders o ON oi.order_id = o.order_id
        WHERE o.order_date < v_cutoff_date
        AND o.status IN ('DELIVERED', 'CANCELLED');
        
        -- Delete from main tables
        DELETE FROM logistics.orders
        WHERE order_date < v_cutoff_date
        AND status IN ('DELIVERED', 'CANCELLED');
        
        -- Log the operation
        INSERT INTO audit.audit_log (table_name, record_id, operation, user_id, new_values)
        VALUES ('orders', 'BATCH_ARCHIVE', 'DELETE', 'SYSTEM', 
                jsonb_build_object('archived_count', v_archived_count, 'cutoff_date', v_cutoff_date));
        
        RAISE NOTICE 'Archived % orders older than %', v_archived_count, v_cutoff_date;
        
    EXCEPTION
        WHEN OTHERS THEN
            RAISE EXCEPTION 'Archive failed: %', SQLERRM;
            ROLLBACK;
    END;
END;
$$;
```

### 7. Triggers

```sql
-- =============================================
-- Trigger: update_timestamp
-- Description: Auto-update updated_at timestamp
-- =============================================

CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    NEW.version = OLD.version + 1;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to all tables with updated_at
CREATE TRIGGER update_customers_updated_at 
    BEFORE UPDATE ON public.customers
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

CREATE TRIGGER update_orders_updated_at 
    BEFORE UPDATE ON logistics.orders
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();
```

```sql
-- =============================================
-- Trigger: audit_trail
-- Description: Create audit records for changes
-- =============================================

CREATE OR REPLACE FUNCTION audit.create_audit_trail()
RETURNS TRIGGER AS $$
DECLARE
    v_old_values JSONB;
    v_new_values JSONB;
    v_changed_fields TEXT[];
BEGIN
    -- Determine operation type
    IF TG_OP = 'DELETE' THEN
        v_old_values := to_jsonb(OLD);
        INSERT INTO audit.audit_log (
            table_name, record_id, operation, user_id, old_values
        ) VALUES (
            TG_TABLE_NAME, OLD.id::TEXT, TG_OP, current_user, v_old_values
        );
        RETURN OLD;
    ELSIF TG_OP = 'UPDATE' THEN
        v_old_values := to_jsonb(OLD);
        v_new_values := to_jsonb(NEW);
        
        -- Find changed fields
        SELECT array_agg(key) INTO v_changed_fields
        FROM jsonb_each(v_old_values) o
        FULL OUTER JOIN jsonb_each(v_new_values) n USING (key)
        WHERE o.value IS DISTINCT FROM n.value;
        
        INSERT INTO audit.audit_log (
            table_name, record_id, operation, user_id, 
            old_values, new_values, changed_fields
        ) VALUES (
            TG_TABLE_NAME, NEW.id::TEXT, TG_OP, current_user,
            v_old_values, v_new_values, v_changed_fields
        );
        RETURN NEW;
    ELSIF TG_OP = 'INSERT' THEN
        v_new_values := to_jsonb(NEW);
        INSERT INTO audit.audit_log (
            table_name, record_id, operation, user_id, new_values
        ) VALUES (
            TG_TABLE_NAME, NEW.id::TEXT, TG_OP, current_user, v_new_values
        );
        RETURN NEW;
    END IF;
END;
$$ LANGUAGE plpgsql;
```

### 8. Security Configuration

```sql
-- =============================================
-- Row Level Security (RLS)
-- Description: Multi-tenant data isolation
-- =============================================

-- Enable RLS on tables
ALTER TABLE public.customers ENABLE ROW LEVEL SECURITY;
ALTER TABLE logistics.orders ENABLE ROW LEVEL SECURITY;

-- Create policies
CREATE POLICY tenant_isolation_customers ON public.customers
    FOR ALL
    TO app_user
    USING (tenant_id = current_setting('app.current_tenant')::UUID);

CREATE POLICY tenant_isolation_orders ON logistics.orders
    FOR ALL
    TO app_user
    USING (
        EXISTS (
            SELECT 1 FROM public.customers c
            WHERE c.customer_id = orders.customer_id
            AND c.tenant_id = current_setting('app.current_tenant')::UUID
        )
    );

-- Grant permissions
GRANT USAGE ON SCHEMA public, logistics, audit TO app_user;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public, logistics TO app_user;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public, logistics TO app_user;
GRANT SELECT ON ALL TABLES IN SCHEMA audit TO app_user;

-- Revoke dangerous permissions
REVOKE DELETE ON public.customers FROM app_user; -- Soft delete only
REVOKE TRUNCATE ON ALL TABLES IN SCHEMA public, logistics FROM app_user;
```

### 9. Performance Optimization

```sql
-- =============================================
-- Performance Tuning Configuration
-- =============================================

-- Table statistics
ALTER TABLE public.customers SET (autovacuum_vacuum_scale_factor = 0.1);
ALTER TABLE logistics.orders SET (autovacuum_analyze_scale_factor = 0.05);

-- Create statistics objects for correlated columns
CREATE STATISTICS customers_location_stats (dependencies) 
ON billing_city, billing_state, billing_country FROM public.customers;

CREATE STATISTICS orders_date_stats (dependencies, ndistinct) 
ON order_date, requested_pickup_date, requested_delivery_date FROM logistics.orders;

-- Partial indexes for common queries
CREATE INDEX idx_orders_recent_active 
ON logistics.orders(order_id, customer_id, status, order_date)
WHERE order_date >= CURRENT_DATE - INTERVAL '30 days'
AND status NOT IN ('DELIVERED', 'CANCELLED');

-- Covering indexes
CREATE INDEX idx_customers_covering 
ON public.customers(customer_id, company_name, status, credit_limit)
INCLUDE (primary_email, created_at)
WHERE deleted_at IS NULL;
```

### 10. Migration Support

```sql
-- =============================================
-- Migration Helpers
-- =============================================

-- Version tracking table
CREATE TABLE IF NOT EXISTS public.schema_versions (
    version_id SERIAL PRIMARY KEY,
    version VARCHAR(20) NOT NULL UNIQUE,
    description TEXT,
    script_name VARCHAR(255),
    applied_by VARCHAR(255) NOT NULL DEFAULT current_user,
    applied_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    execution_time INTERVAL,
    success BOOLEAN NOT NULL DEFAULT TRUE,
    error_message TEXT
);

-- Migration template
/*
-- Migration: V1.0.0__initial_schema.sql
-- Description: Initial schema creation
-- Author: [Your Name]
-- Date: YYYY-MM-DD

DO $$
DECLARE
    v_start_time TIMESTAMP := clock_timestamp();
    v_version VARCHAR(20) := 'V1.0.0';
BEGIN
    -- Check if already applied
    IF EXISTS (SELECT 1 FROM public.schema_versions WHERE version = v_version) THEN
        RAISE NOTICE 'Migration % already applied', v_version;
        RETURN;
    END IF;
    
    -- Apply migration
    -- [Your DDL statements here]
    
    -- Record successful migration
    INSERT INTO public.schema_versions (version, description, script_name, execution_time)
    VALUES (v_version, 'Initial schema creation', 'V1.0.0__initial_schema.sql', 
            clock_timestamp() - v_start_time);
            
    RAISE NOTICE 'Migration % completed successfully', v_version;
EXCEPTION
    WHEN OTHERS THEN
        -- Record failed migration
        INSERT INTO public.schema_versions (version, description, script_name, success, error_message)
        VALUES (v_version, 'Initial schema creation', 'V1.0.0__initial_schema.sql', FALSE, SQLERRM);
        
        RAISE;
END $$;
*/
```

## Traceability Instructions

1. **DRD Mapping**: Every table/column traces to DRD entities/attributes
2. **Performance Requirements**: Indexes support NFR performance targets
3. **Security Implementation**: RLS and permissions implement security requirements
4. **Audit Requirements**: Triggers and audit tables fulfill compliance needs
5. **Data Integrity**: Constraints enforce business rules from FRD

## Quality Criteria

Your DB-SCHEMA must:
- Implement all entities from DRD
- Include complete DDL statements
- Define all constraints and relationships
- Optimize for identified access patterns
- Include security configurations
- Provide migration support
- Document all objects clearly
- Follow naming conventions consistently

## Output Format

Provide the complete DB-SCHEMA in Markdown format with:
- Proper YAML frontmatter
- Executable SQL statements
- Clear documentation comments
- Performance optimization notes
- Security configurations
- Migration templates

## Chain-of-Thought Instructions

When creating the schema:
1. Map DRD logical model to physical tables
2. Choose appropriate data types
3. Define all constraints
4. Create indexes for performance
5. Add audit/history support
6. Implement security measures
7. Plan for migrations
8. Document thoroughly
```

## Iterative Refinement Prompts

### Refinement Round 1: Completeness
```markdown
Review the DB-SCHEMA and enhance it by:
1. Ensuring all DRD entities are implemented
2. Verifying all relationships have foreign keys
3. Adding missing constraints
4. Including all required indexes
5. Checking audit trail completeness
```

### Refinement Round 2: Performance
```markdown
Refine the DB-SCHEMA by:
1. Analyzing query patterns and adding indexes
2. Considering partitioning strategies
3. Adding materialized views for reports
4. Optimizing data types for storage
5. Including database-specific optimizations
```

### Refinement Round 3: Operations
```markdown
Enhance the DB-SCHEMA by:
1. Adding maintenance procedures
2. Including backup considerations
3. Defining archival strategies
4. Adding monitoring queries
5. Creating diagnostic views

## Iterative Requirements Elicitation

After generating the initial Database Schema Document, perform a comprehensive analysis to identify gaps, ambiguities, and areas requiring clarification. Create a structured list of questions for the client that will help refine and complete the DB requirements.

### 7. Client Clarification Questions

Think critically about database design, table structures, relationships, indexes, constraints, and data integrity that might not have been fully considered or might be unclear. Generate specific, actionable questions organized by category:

```yaml
id: DB-QUESTION-001
category: [Table Design|Relationships|Indexes|Constraints|Data Types|Performance|Security|Migration|Other]
question: [Specific question for the client]
rationale: [Why this question is important for DB success]
related_requirements: [DB-XXX, DRD-XXX, or FRD-XXX references if applicable]
priority: High|Medium|Low
expected_impact: [How the answer will affect the DB requirements]
```

#### Question Categories:

**DB-Specific Questions:**
- Clarifications on database schema, table relationships, indexing strategies, and data integrity rules
- Edge cases and exception scenarios
- Integration and dependency requirements
- Performance and quality expectations
- Compliance and governance needs

### Instructions for Question Generation:

1. **Be Specific**: Ask precise questions that will yield actionable answers
2. **Prioritize Impact**: Focus on questions that will significantly affect DB requirements
3. **Consider Edge Cases**: Think about unusual scenarios and exceptions
4. **Validate Assumptions**: Question any assumptions made in the initial requirements
5. **Ensure Completeness**: Look for gaps in database schema, table relationships, indexing strategies, and data integrity rules
6. **Think Downstream**: Consider how answers will affect implementation
7. **Maintain Traceability**: Link questions to specific requirements when applicable

### Answer Integration Process:

When client answers are received, they should be integrated back into the Database Schema Document using this process:

1. **Create Answer Records**:
```yaml
id: DB-ANSWER-001
question_id: DB-QUESTION-001
answer: [Client's response]
provided_by: [Stakeholder name/role]
date_received: YYYY-MM-DD
impact_assessment: [How this affects existing requirements]
```

2. **Update Affected Requirements**: Modify existing requirements based on answers
3. **Create New Requirements**: Add new requirements identified through answers
4. **Update Traceability**: Ensure all changes maintain proper traceability links
5. **Document Changes**: Track what was modified and why

This iterative approach ensures comprehensive DB requirements that address all critical aspects and reduce implementation risks.

```

## Validation Checklist

Before finalizing the DB-SCHEMA, ensure:

- [ ] All DRD entities have corresponding tables
- [ ] Primary keys are defined for all tables
- [ ] Foreign key relationships are complete
- [ ] Appropriate indexes for all access patterns
- [ ] Check constraints enforce business rules
- [ ] Audit triggers capture all changes
- [ ] Security policies implement access control
- [ ] Views provide necessary abstractions
- [ ] Functions encapsulate business logic
- [ ] Migration strategy is defined

## Pro Tips for LLM Users

1. **Start with DRD**: Use logical model as foundation
2. **Think Performance**: Design indexes alongside tables
3. **Security First**: Include RLS and permissions
4. **Maintainability**: Use clear naming and comments
5. **Operations Ready**: Include maintenance procedures
6. **Migration Path**: Plan for schema evolution
7. **Test Data**: Consider including sample data scripts

## Example Usage

```markdown
Generate a DB-SCHEMA using this template with the following context:
- DRD: [Complete data requirements with entities]
- TRD: "PostgreSQL 15, expecting 1M orders/month..."
- Access Patterns: "Frequent queries by date range, customer..."
- Security: "Multi-tenant with row-level isolation..."
- Performance: "Sub-100ms query response required..."
[Continue with all required inputs]