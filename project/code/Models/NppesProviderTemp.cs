using System.ComponentModel.DataAnnotations;

using System;
namespace ByteForgeFrontend.Models;

public class NppesProviderTemp
{
    [Key]
    public long Id { get; set; }
    
    [StringLength(10)]
    public string? NPI { get; set; }
    
    [StringLength(200)]
    public string? FirstName { get; set; }
    
    [StringLength(200)]
    public string? LastName { get; set; }
    
    [StringLength(200)]
    public string? BusinessName { get; set; }
    
    [StringLength(200)]
    public string? PracticeAddress1 { get; set; }
    
    [StringLength(200)]
    public string? PracticeAddress2 { get; set; }
    
    [StringLength(100)]
    public string? PracticeCity { get; set; }
    
    [StringLength(2)]
    public string? PracticeState { get; set; }
    
    [StringLength(20)]
    public string? PracticePostalCode { get; set; }
    
    [StringLength(50)]
    public string? PracticeCountry { get; set; }
    
    [StringLength(20)]
    public string? PracticeTelephone { get; set; }
    
    [StringLength(500)]
    public string? Specialties { get; set; }
    
    [StringLength(10)]
    public string? ProviderTaxonomyCode1 { get; set; }
    
    [StringLength(200)]
    public string? ProviderOrganizationName { get; set; }
    
    [StringLength(200)]
    public string? ProviderLastName { get; set; }
    
    [StringLength(200)]
    public string? ProviderFirstName { get; set; }
    
    [StringLength(1)]
    public string? ProviderGenderCode { get; set; }
    
    public DateTime? ProviderEnumerationDate { get; set; }
    
    [StringLength(20)]
    public string? ProviderBusinessPracticeLocationAddressTelephoneNumber { get; set; }
    
    [StringLength(50)]
    public string? ProviderBusinessPracticeLocationAddressStateName { get; set; }
    
    [StringLength(200)]
    public string? ProviderBusinessPracticeLocationAddressCityName { get; set; }
    
    [StringLength(20)]
    public string? ProviderBusinessPracticeLocationAddressPostalCode { get; set; }
    
    [StringLength(200)]
    public string? ProviderBusinessPracticeLocationAddressLine1 { get; set; }
    
    [StringLength(200)]
    public string? ProviderBusinessPracticeLocationAddressLine2 { get; set; }
    
    [StringLength(100)]
    public string? TaxonomyDescription1 { get; set; }
    
    public DateTime? LastUpdateDate { get; set; }
    
    public DateTime ImportDate { get; set; } = DateTime.UtcNow;
    
    public bool IsProcessed { get; set; } = false;
    
    public DateTime? ImportedDate { get; set; }
    
    [StringLength(2)]
    public string? EntityTypeCode { get; set; }
    
    [StringLength(400)]
    public string? ComputedFullName { get; set; }
    
    [StringLength(500)]
    public string? ComputedBusinessAddress { get; set; }
}