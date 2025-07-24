using Microsoft.AspNetCore.Identity.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore;
using ByteForgeFrontend.Models;
using ByteForgeFrontend.Models.ProjectManagement;
using ByteForgeFrontend.Models.Security;
using System.Text.Json;

using System.Collections.Generic;
namespace ByteForgeFrontend.Data;

public class ApplicationDbContext : IdentityDbContext<ApplicationUser>
{
    public ApplicationDbContext(DbContextOptions<ApplicationDbContext> options)
        : base(options)
    {
    }

    // ByteForge entities only - removed old lead processing entities
    public DbSet<Project> Projects { get; set; } = null!;
    public DbSet<ProjectDocument> ProjectDocuments { get; set; } = null!;
    public DbSet<ProjectTemplate> ProjectTemplates { get; set; } = null!;
    
    // Security entities
    public DbSet<ApiKey> ApiKeys { get; set; } = null!;
    public DbSet<ApiKeyAuditLog> ApiKeyAuditLogs { get; set; } = null!;
    public DbSet<AuditLog> AuditLogs { get; set; } = null!;
    public DbSet<DataRetentionPolicy> DataRetentionPolicies { get; set; } = null!;
    public DbSet<TenantSecurityConfiguration> TenantSecurityConfigurations { get; set; } = null!;
    public DbSet<AccessControlPolicy> AccessControlPolicies { get; set; } = null!;
    public DbSet<ComplianceReview> ComplianceReviews { get; set; } = null!;
    
    // Job scheduling entities
    public DbSet<JobScheduleSettings> JobScheduleSettings { get; set; } = null!;
    
    // Lead processing entities
    public DbSet<Lead> Leads { get; set; } = null!;
    public DbSet<WorkflowSettings> WorkflowSettings { get; set; } = null!;
    
    // NPPES entities
    public DbSet<NppesFilterConfiguration> NppesFilterConfigurations { get; set; } = null!;
    public DbSet<NppesProviderTemp> NppesProviderTemp { get; set; } = null!;

    protected override void OnModelCreating(ModelBuilder builder)
    {
        base.OnModelCreating(builder);
        
        // Old lead processing entity configurations removed
        
        // Configure Project entity
        builder.Entity<Project>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.Property(e => e.Name).IsRequired().HasMaxLength(200);
            entity.Property(e => e.Description).HasMaxLength(1000);
            entity.Property(e => e.TemplateId).HasMaxLength(50);
            entity.Property(e => e.CreatedBy).HasMaxLength(200);
            
            // Convert Metadata dictionary to JSON
            entity.Property(e => e.Metadata)
                .HasConversion(
                    v => JsonSerializer.Serialize(v, (JsonSerializerOptions)null!),
                    v => JsonSerializer.Deserialize<Dictionary<string, object>>(v, (JsonSerializerOptions)null!) ?? new Dictionary<string, object>()
                );
            
            // Add unique constraint on Name
            entity.HasIndex(e => e.Name).IsUnique();
            
            // Configure relationship with documents
            entity.HasMany(e => e.Documents)
                .WithOne(d => d.Project)
                .HasForeignKey(d => d.ProjectId)
                .OnDelete(DeleteBehavior.Cascade);
        });
        
        // Configure ProjectDocument entity
        builder.Entity<ProjectDocument>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.Property(e => e.DocumentType).IsRequired().HasMaxLength(50);
            entity.Property(e => e.Content).IsRequired();
            entity.Property(e => e.Version).HasMaxLength(20);
            entity.Property(e => e.CreatedBy).HasMaxLength(200);
            
            // Convert Metadata dictionary to JSON
            entity.Property(e => e.Metadata)
                .HasConversion(
                    v => JsonSerializer.Serialize(v, (JsonSerializerOptions)null!),
                    v => JsonSerializer.Deserialize<Dictionary<string, object>>(v, (JsonSerializerOptions)null!) ?? new Dictionary<string, object>()
                );
            
            // Index for faster queries
            entity.HasIndex(e => e.ProjectId);
            entity.HasIndex(e => new { e.ProjectId, e.DocumentType });
        });
        
        // Configure ProjectTemplate entity
        builder.Entity<ProjectTemplate>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.Property(e => e.Id).HasMaxLength(50);
            entity.Property(e => e.Name).IsRequired().HasMaxLength(200);
            entity.Property(e => e.Description).HasMaxLength(1000);
            entity.Property(e => e.Category).HasMaxLength(50);
            entity.Property(e => e.Version).HasMaxLength(20);
            
            // Convert arrays to JSON
            entity.Property(e => e.RequiredDocuments)
                .HasConversion(
                    v => JsonSerializer.Serialize(v, (JsonSerializerOptions)null!),
                    v => JsonSerializer.Deserialize<string[]>(v, (JsonSerializerOptions)null!) ?? Array.Empty<string>()
                );
                
            entity.Property(e => e.OptionalDocuments)
                .HasConversion(
                    v => JsonSerializer.Serialize(v, (JsonSerializerOptions)null!),
                    v => JsonSerializer.Deserialize<string[]>(v, (JsonSerializerOptions)null!) ?? Array.Empty<string>()
                );
            
            // Convert dictionaries to JSON
            entity.Property(e => e.DefaultSettings)
                .HasConversion(
                    v => JsonSerializer.Serialize(v, (JsonSerializerOptions)null!),
                    v => JsonSerializer.Deserialize<Dictionary<string, object>>(v, (JsonSerializerOptions)null!) ?? new Dictionary<string, object>()
                );
                
            entity.Property(e => e.FileStructure)
                .HasConversion(
                    v => JsonSerializer.Serialize(v, (JsonSerializerOptions)null!),
                    v => JsonSerializer.Deserialize<Dictionary<string, string>>(v, (JsonSerializerOptions)null!) ?? new Dictionary<string, string>()
                );
            
            // Add unique constraint on Id
            entity.HasIndex(e => e.Id).IsUnique();
            
            // Index for category queries
            entity.HasIndex(e => e.Category);
        });
        
        // Configure security entities
        ConfigureSecurityEntities(builder);
    }
    
    private void ConfigureSecurityEntities(ModelBuilder builder)
    {
        // Configure ApiKey entity
        builder.Entity<ApiKey>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.Property(e => e.Name).IsRequired().HasMaxLength(200);
            entity.Property(e => e.KeyPrefix).IsRequired().HasMaxLength(50);
            entity.Property(e => e.EncryptedValue).IsRequired();
            entity.Property(e => e.DeletedBy).HasMaxLength(200);
            
            // Convert Metadata dictionary to JSON
            entity.Property(e => e.Metadata)
                .HasConversion(
                    v => JsonSerializer.Serialize(v, (JsonSerializerOptions)null!),
                    v => JsonSerializer.Deserialize<Dictionary<string, string>>(v, (JsonSerializerOptions)null!) ?? new Dictionary<string, string>()
                );
            
            // Configure soft delete query filter
            entity.HasQueryFilter(e => !e.IsDeleted);
            
            // Index for faster queries
            entity.HasIndex(e => e.TenantId);
            entity.HasIndex(e => new { e.TenantId, e.KeyType });
            entity.HasIndex(e => e.UserId);
            
            // Configure relationship with ApplicationUser
            entity.HasOne(e => e.User)
                .WithMany(u => u.ApiKeys)
                .HasForeignKey(e => e.UserId)
                .OnDelete(DeleteBehavior.Restrict);
        });
        
        // Configure ApiKeyAuditLog entity
        builder.Entity<ApiKeyAuditLog>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.Property(e => e.Action).IsRequired().HasMaxLength(100);
            entity.Property(e => e.PerformedBy).HasMaxLength(200);
            entity.Property(e => e.IpAddress).HasMaxLength(50);
            entity.Property(e => e.UserAgent).HasMaxLength(500);
            
            // Convert Details dictionary to JSON
            entity.Property(e => e.Details)
                .HasConversion(
                    v => JsonSerializer.Serialize(v, (JsonSerializerOptions)null!),
                    v => JsonSerializer.Deserialize<Dictionary<string, object>>(v, (JsonSerializerOptions)null!) ?? new Dictionary<string, object>()
                );
            
            // Index for faster queries
            entity.HasIndex(e => e.ApiKeyId);
            entity.HasIndex(e => e.TenantId);
            
            // Configure relationship with ApiKey
            entity.HasOne(e => e.ApiKey)
                .WithMany(k => k.AuditLogs)
                .HasForeignKey(e => e.ApiKeyId)
                .OnDelete(DeleteBehavior.Cascade);
        });
        
        // Configure AuditLog entity
        builder.Entity<AuditLog>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.Property(e => e.Action).IsRequired().HasMaxLength(100);
            entity.Property(e => e.Resource).IsRequired().HasMaxLength(100);
            entity.Property(e => e.ResourceId).HasMaxLength(200);
            entity.Property(e => e.IpAddress).HasMaxLength(50);
            entity.Property(e => e.UserAgent).HasMaxLength(500);
            
            // Convert Details dictionary to JSON
            entity.Property(e => e.Details)
                .HasConversion(
                    v => JsonSerializer.Serialize(v, (JsonSerializerOptions)null!),
                    v => JsonSerializer.Deserialize<Dictionary<string, object>>(v, (JsonSerializerOptions)null!) ?? new Dictionary<string, object>()
                );
            
            // Configure query filter for archived logs
            entity.HasQueryFilter(e => !e.IsArchived);
            
            // Index for faster queries
            entity.HasIndex(e => e.TenantId);
            entity.HasIndex(e => new { e.TenantId, e.UserId });
            entity.HasIndex(e => new { e.TenantId, e.Resource });
            entity.HasIndex(e => new { e.TenantId, e.LogType });
            entity.HasIndex(e => e.Timestamp);
        });
        
        // Configure DataRetentionPolicy entity
        builder.Entity<DataRetentionPolicy>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.Property(e => e.DataType).IsRequired().HasMaxLength(100);
            
            // Index for faster queries
            entity.HasIndex(e => e.TenantId);
            entity.HasIndex(e => new { e.TenantId, e.DataType }).IsUnique();
        });
        
        // Configure TenantSecurityConfiguration entity
        builder.Entity<TenantSecurityConfiguration>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.Property(e => e.PasswordComplexityRules).HasMaxLength(500);
            
            // Convert WhitelistedIPs list to JSON
            entity.Property(e => e.WhitelistedIPs)
                .HasConversion(
                    v => JsonSerializer.Serialize(v, (JsonSerializerOptions)null!),
                    v => JsonSerializer.Deserialize<List<string>>(v, (JsonSerializerOptions)null!) ?? new List<string>()
                );
            
            // Unique constraint on TenantId
            entity.HasIndex(e => e.TenantId).IsUnique();
        });
        
        // Configure AccessControlPolicy entity
        builder.Entity<AccessControlPolicy>(entity =>
        {
            entity.HasKey(e => e.Id);
            
            // Unique constraint on TenantId
            entity.HasIndex(e => e.TenantId).IsUnique();
        });
        
        // Configure ComplianceReview entity
        builder.Entity<ComplianceReview>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.Property(e => e.AssignedTo).HasMaxLength(200);
            
            // Convert lists and dictionaries to JSON
            entity.Property(e => e.ReviewTasks)
                .HasConversion(
                    v => JsonSerializer.Serialize(v, (JsonSerializerOptions)null!),
                    v => JsonSerializer.Deserialize<List<string>>(v, (JsonSerializerOptions)null!) ?? new List<string>()
                );
                
            entity.Property(e => e.Results)
                .HasConversion(
                    v => JsonSerializer.Serialize(v, (JsonSerializerOptions)null!),
                    v => JsonSerializer.Deserialize<Dictionary<string, object>>(v, (JsonSerializerOptions)null!) ?? new Dictionary<string, object>()
                );
            
            // Index for faster queries
            entity.HasIndex(e => e.TenantId);
            entity.HasIndex(e => new { e.TenantId, e.Status });
        });
    }
}