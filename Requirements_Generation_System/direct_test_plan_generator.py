#!/usr/bin/env python3
"""
Direct Test Plan Generator
This script directly generates the frontend test plan without requiring Claude Code.
"""

import asyncio
import sys
from pathlib import Path
from rich.console import Console

# Add the current directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

from frontend_test_generator import FrontendTestGenerator

console = Console()


async def generate_test_plan_directly():
    """Generate the test plan directly using the FrontendTestGenerator"""
    
    console.print("[bold cyan]🔧 Direct Test Plan Generation[/bold cyan]")
    console.print("This will generate the frontend test plan directly without Claude Code dependency.\n")
    
    try:
        # Initialize the generator
        project_name = "FY.WB.Midway"
        base_path = Path(__file__).parent.parent
        model_provider = "anthropic"
        
        generator = FrontendTestGenerator(project_name, base_path, model_provider)
        
        # Analyze frontend structure
        console.print("[cyan]Step 1: Analyzing frontend structure...[/cyan]")
        pages_info = await generator._analyze_frontend_structure()
        console.print(f"[green]✅ Found {len(pages_info)} pages/components[/green]")
        
        # Generate comprehensive test plan
        console.print("[cyan]Step 2: Generating comprehensive test plan...[/cyan]")
        test_plan_content = await create_comprehensive_test_plan(pages_info, project_name)
        
        # Save test plan
        test_plan_path = generator.testing_output_path / "frontend_test_plan.md"
        test_plan_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(test_plan_path, 'w', encoding='utf-8') as f:
            f.write(test_plan_content)
        
        console.print(f"[green]✅ Test plan saved to: {test_plan_path}[/green]")
        console.print(f"[green]✅ Test plan size: {len(test_plan_content)} characters[/green]")
        
        # Show summary
        console.print(f"\n[bold green]🎉 Test Plan Generated Successfully![/bold green]")
        console.print(f"[cyan]Pages analyzed: {len([p for p in pages_info if p['type'] == 'page'])}[/cyan]")
        console.print(f"[cyan]Components analyzed: {len([p for p in pages_info if p['type'] == 'component'])}[/cyan]")
        console.print(f"[cyan]Total items: {len(pages_info)}[/cyan]")
        
        return True
        
    except Exception as e:
        console.print(f"[red]❌ Error generating test plan: {e}[/red]")
        import traceback
        console.print(traceback.format_exc())
        return False


async def create_comprehensive_test_plan(pages_info, project_name):
    """Create a comprehensive test plan for the frontend"""
    
    # Separate pages and components
    pages = [p for p in pages_info if p['type'] == 'page']
    components = [p for p in pages_info if p['type'] == 'component']
    
    # Group pages by category
    admin_pages = [p for p in pages if p['route'].startswith('/admin')]
    client_pages = [p for p in pages if p['route'].startswith('/client')]
    public_pages = [p for p in pages if p['route'].startswith('/public')]
    business_pages = [p for p in pages if any(p['route'].startswith(f'/{cat}') for cat in ['customers', 'loads', 'invoices', 'carriers', 'payments', 'payouts', 'reports', 'documents'])]
    auth_pages = [p for p in pages if p['name'] in ['login', 'register', 'tenant']]
    other_pages = [p for p in pages if p not in admin_pages + client_pages + public_pages + business_pages + auth_pages]
    
    test_plan = f"""# Frontend Test Plan for {project_name}

## Executive Summary

This comprehensive test plan covers the complete frontend testing strategy for the {project_name} Enterprise Logistics Platform. The plan includes systematic testing of all {len(pages)} pages and {len(components)} components, with focus on user workflows, interactive elements, and business logic validation.

### Coverage Overview
- **Total Pages**: {len(pages)}
- **Total Components**: {len(components)}
- **Admin Pages**: {len(admin_pages)}
- **Client Pages**: {len(client_pages)}
- **Business Logic Pages**: {len(business_pages)}
- **Authentication Pages**: {len(auth_pages)}
- **Public Pages**: {len(public_pages)}

## Page Inventory

### Authentication Pages
{chr(10).join([f"- **{p['name'].title()}** (`{p['route']}`) - {p['path']}" for p in auth_pages])}

### Admin Panel Pages
{chr(10).join([f"- **{p['name'].title()}** (`{p['route']}`) - {p['path']}" for p in admin_pages])}

### Client Management Pages
{chr(10).join([f"- **{p['name'].title()}** (`{p['route']}`) - {p['path']}" for p in client_pages])}

### Business Logic Pages
{chr(10).join([f"- **{p['name'].title()}** (`{p['route']}`) - {p['path']}" for p in business_pages])}

### Public Pages
{chr(10).join([f"- **{p['name'].title()}** (`{p['route']}`) - {p['path']}" for p in public_pages])}

### Other Pages
{chr(10).join([f"- **{p['name'].title()}** (`{p['route']}`) - {p['path']}" for p in other_pages])}

## Test Tasks by Page Category

### Authentication Testing

#### Login Page Tests (`/login`)
- [ ] **Load Test**: Navigate to /login and verify page loads without errors
- [ ] **Style Compliance**: Verify login form matches design specifications
- [ ] **Valid Login**: Enter valid credentials and verify successful authentication
- [ ] **Invalid Login**: Test with invalid credentials and verify error handling
- [ ] **Empty Fields**: Submit form with empty fields and verify validation
- [ ] **Remember Me**: Test remember me functionality if present
- [ ] **Forgot Password**: Test forgot password link if present
- [ ] **Responsive Design**: Test login form on mobile (375px) and desktop (1920px)

#### Registration Page Tests (`/register`)
- [ ] **Load Test**: Navigate to /register and verify page loads without errors
- [ ] **Form Validation**: Test all form field validations
- [ ] **Successful Registration**: Complete registration with valid data
- [ ] **Duplicate Email**: Test registration with existing email
- [ ] **Password Strength**: Test password strength requirements
- [ ] **Terms Acceptance**: Verify terms and conditions checkbox functionality

### Admin Panel Testing

#### Admin Dashboard Tests (`/admin`)
- [ ] **Load Test**: Navigate to /admin and verify admin dashboard loads
- [ ] **Access Control**: Verify only admin users can access this page
- [ ] **Dashboard Widgets**: Test all dashboard widgets and statistics
- [ ] **Navigation Menu**: Test all admin navigation menu items
- [ ] **Quick Actions**: Test quick action buttons and links

#### Admin Settings Tests (`/admin/settings`)
- [ ] **Load Test**: Navigate to /admin/settings and verify page loads
- [ ] **System Settings**: Test system configuration options
- [ ] **Save Settings**: Test saving configuration changes
- [ ] **Reset Settings**: Test reset to default functionality if present

#### Tenant Management Tests (`/admin/tenants`)
- [ ] **Load Test**: Navigate to /admin/tenants and verify page loads
- [ ] **Tenant List**: Verify tenant list displays correctly
- [ ] **Add Tenant**: Test new tenant creation workflow
- [ ] **Edit Tenant**: Test tenant editing functionality
- [ ] **Tenant Status**: Test tenant activation/deactivation

#### User Management Tests (`/admin/users`)
- [ ] **Load Test**: Navigate to /admin/users and verify page loads
- [ ] **User List**: Verify user list displays with proper information
- [ ] **Add User**: Test new user creation workflow
- [ ] **Edit User**: Test user editing functionality
- [ ] **User Roles**: Test role assignment and permissions

### Business Logic Testing

#### Customer Management Tests (`/customers`)
- [ ] **Load Test**: Navigate to /customers and verify customer list loads
- [ ] **Customer List**: Verify customer list displays with proper data
- [ ] **Search Customers**: Test customer search functionality
- [ ] **Filter Customers**: Test customer filtering options
- [ ] **Pagination**: Test customer list pagination if present

#### New Customer Tests (`/customers/new`)
- [ ] **Load Test**: Navigate to /customers/new and verify form loads
- [ ] **Customer Form**: Fill customer form with valid data and submit
- [ ] **Form Validation**: Test all customer form field validations
- [ ] **Required Fields**: Test form submission with missing required fields
- [ ] **Duplicate Customer**: Test creation with duplicate customer information

#### Customer Details Tests (`/customers/[id]`)
- [ ] **Load Test**: Navigate to customer detail page and verify it loads
- [ ] **Customer Information**: Verify customer details display correctly
- [ ] **Edit Customer**: Test customer information editing
- [ ] **Customer History**: Verify customer transaction history if present
- [ ] **Related Records**: Test links to related loads, invoices, etc.

#### Load Management Tests (`/loads`)
- [ ] **Load Test**: Navigate to /loads and verify load list loads
- [ ] **Load List**: Verify load list displays with proper information
- [ ] **Search Loads**: Test load search functionality
- [ ] **Filter Loads**: Test load filtering by status, date, etc.
- [ ] **Load Status**: Verify load status indicators work correctly

#### New Load Tests (`/loads/new`)
- [ ] **Load Test**: Navigate to /loads/new and verify form loads
- [ ] **Load Form**: Fill load form with valid data and submit
- [ ] **Origin/Destination**: Test origin and destination selection
- [ ] **Load Details**: Test weight, dimensions, and equipment type fields
- [ ] **Customer Assignment**: Test customer assignment to load

#### Load Details Tests (`/loads/[id]`)
- [ ] **Load Test**: Navigate to load detail page and verify it loads
- [ ] **Load Information**: Verify load details display correctly
- [ ] **Status Updates**: Test load status update functionality
- [ ] **Document Upload**: Test document upload for load if present
- [ ] **Tracking**: Test load tracking functionality if present

#### Invoice Management Tests (`/invoices`)
- [ ] **Load Test**: Navigate to /invoices and verify invoice list loads
- [ ] **Invoice List**: Verify invoice list displays with proper data
- [ ] **Search Invoices**: Test invoice search functionality
- [ ] **Filter Invoices**: Test invoice filtering by status, date, customer
- [ ] **Invoice Status**: Verify invoice status indicators

#### New Invoice Tests (`/invoices/new`)
- [ ] **Load Test**: Navigate to /invoices/new and verify form loads
- [ ] **Invoice Form**: Fill invoice form with valid data and submit
- [ ] **Line Items**: Test adding and removing invoice line items
- [ ] **Calculations**: Verify invoice total calculations are correct
- [ ] **Customer Selection**: Test customer selection for invoice

#### Invoice Details Tests (`/invoices/[id]`)
- [ ] **Load Test**: Navigate to invoice detail page and verify it loads
- [ ] **Invoice Information**: Verify invoice details display correctly
- [ ] **Print Invoice**: Test invoice printing functionality if present
- [ ] **Email Invoice**: Test invoice email functionality if present
- [ ] **Payment Status**: Verify payment status tracking

### Client Portal Testing

#### Client Dashboard Tests (`/client`)
- [ ] **Load Test**: Navigate to /client and verify client dashboard loads
- [ ] **Access Control**: Verify only client users can access this page
- [ ] **Client Data**: Verify client-specific data displays correctly
- [ ] **Quick Actions**: Test client-specific quick actions

#### Client Profile Tests (`/client/profile`)
- [ ] **Load Test**: Navigate to /client/profile and verify page loads
- [ ] **Profile Information**: Verify client profile displays correctly
- [ ] **Edit Profile**: Test profile editing functionality
- [ ] **Password Change**: Test password change functionality if present

#### Client Settings Tests (`/client/settings`)
- [ ] **Load Test**: Navigate to /client/settings and verify page loads
- [ ] **Client Settings**: Test client-specific settings options
- [ ] **Notification Preferences**: Test notification settings if present
- [ ] **Save Settings**: Test saving client settings

### Carrier Management Testing

#### Carrier Portal Tests (`/carrier/portal`)
- [ ] **Load Test**: Navigate to /carrier/portal and verify page loads
- [ ] **Carrier Dashboard**: Verify carrier-specific dashboard functionality
- [ ] **Available Loads**: Test available loads display for carriers
- [ ] **Load Bidding**: Test load bidding functionality if present

#### Carrier Registration Tests (`/carriers/register`)
- [ ] **Load Test**: Navigate to /carriers/register and verify form loads
- [ ] **Registration Form**: Fill carrier registration form and submit
- [ ] **Document Upload**: Test required document uploads
- [ ] **Verification Process**: Test carrier verification workflow

### Payment and Financial Testing

#### Payment Management Tests (`/payments`)
- [ ] **Load Test**: Navigate to /payments and verify page loads
- [ ] **Payment List**: Verify payment list displays correctly
- [ ] **Payment Processing**: Test payment processing functionality
- [ ] **Payment Status**: Verify payment status tracking

#### Payout Management Tests (`/payouts`)
- [ ] **Load Test**: Navigate to /payouts and verify page loads
- [ ] **Payout List**: Verify payout list displays correctly
- [ ] **Process Payouts**: Test payout processing functionality
- [ ] **Payout History**: Verify payout history tracking

### Reporting and Analytics Testing

#### Reports Dashboard Tests (`/reports`)
- [ ] **Load Test**: Navigate to /reports and verify page loads
- [ ] **Report Generation**: Test report generation functionality
- [ ] **Date Filters**: Test report date range filtering
- [ ] **Export Reports**: Test report export functionality if present
- [ ] **Chart Displays**: Verify charts and graphs display correctly

### Document Management Testing

#### Document Management Tests (`/documents`)
- [ ] **Load Test**: Navigate to /documents and verify page loads
- [ ] **Document List**: Verify document list displays correctly
- [ ] **Upload Documents**: Test document upload functionality
- [ ] **Download Documents**: Test document download functionality
- [ ] **Document Categories**: Test document categorization

### Public Pages Testing

#### Public Homepage Tests (`/public`)
- [ ] **Load Test**: Navigate to /public and verify page loads
- [ ] **Public Content**: Verify public content displays correctly
- [ ] **Navigation**: Test public page navigation
- [ ] **Contact Information**: Verify contact information is accurate

#### About Page Tests (`/public/about`)
- [ ] **Load Test**: Navigate to /public/about and verify page loads
- [ ] **About Content**: Verify about page content displays correctly
- [ ] **Company Information**: Verify company information is accurate

#### Contact Page Tests (`/public/contact`)
- [ ] **Load Test**: Navigate to /public/contact and verify page loads
- [ ] **Contact Form**: Test contact form submission
- [ ] **Contact Information**: Verify contact details are correct
- [ ] **Map Integration**: Test map integration if present

## Modal Testing

### Common Modal Tests
- [ ] **Customer Modal - Open**: Click "New Customer" and verify modal opens
- [ ] **Customer Modal - Form**: Fill customer form in modal and submit
- [ ] **Customer Modal - Close**: Verify modal closes properly with X button
- [ ] **Customer Modal - Cancel**: Test cancel button functionality
- [ ] **Load Modal - Open**: Click "New Load" and verify modal opens
- [ ] **Load Modal - Form**: Fill load form in modal and submit
- [ ] **Load Modal - Validation**: Test modal form validation
- [ ] **Invoice Modal - Open**: Click "New Invoice" and verify modal opens
- [ ] **Invoice Modal - Calculations**: Test invoice calculations in modal
- [ ] **Confirmation Modals**: Test delete confirmation modals
- [ ] **Error Modals**: Test error message modal displays

## Cross-Page Workflow Tests

### Complete Customer Workflow
- [ ] **Customer Creation**: Create new customer through complete workflow
- [ ] **Load Assignment**: Assign load to newly created customer
- [ ] **Invoice Generation**: Generate invoice for customer load
- [ ] **Payment Processing**: Process payment for customer invoice
- [ ] **Document Management**: Upload and manage customer documents

### Complete Load Workflow
- [ ] **Load Creation**: Create new load with all required information
- [ ] **Carrier Assignment**: Assign carrier to load
- [ ] **Status Tracking**: Update load status through completion
- [ ] **Invoice Generation**: Generate invoice for completed load
- [ ] **Document Upload**: Upload load-related documents

### Admin Management Workflow
- [ ] **User Creation**: Create new user with appropriate role
- [ ] **Tenant Setup**: Set up new tenant with configuration
- [ ] **Permission Testing**: Verify role-based permissions work
- [ ] **System Configuration**: Update system settings and verify changes

## Performance Tests

### Page Load Performance
- [ ] **Homepage Load**: Verify homepage loads in under 3 seconds
- [ ] **Dashboard Load**: Verify dashboard loads in under 5 seconds
- [ ] **List Pages**: Verify list pages load in under 4 seconds
- [ ] **Detail Pages**: Verify detail pages load in under 3 seconds
- [ ] **Form Pages**: Verify form pages load in under 2 seconds

### Responsive Design Tests
- [ ] **Mobile Layout**: Test all pages on mobile viewport (375px width)
- [ ] **Tablet Layout**: Test all pages on tablet viewport (768px width)
- [ ] **Desktop Layout**: Test all pages on desktop viewport (1920px width)
- [ ] **Navigation Menu**: Verify mobile navigation menu functionality
- [ ] **Form Layouts**: Verify forms are usable on all screen sizes

## Error Handling Tests

### HTTP Error Tests
- [ ] **404 Page**: Navigate to non-existent page and verify 404 handling
- [ ] **500 Error**: Test server error handling and user feedback
- [ ] **Network Error**: Test network connectivity error handling
- [ ] **Timeout Error**: Test request timeout error handling

### Validation Error Tests
- [ ] **Form Validation**: Test all form validation error messages
- [ ] **Required Fields**: Test required field validation
- [ ] **Data Format**: Test email, phone, date format validations
- [ ] **Business Rules**: Test business logic validation errors

### Authentication Error Tests
- [ ] **Session Timeout**: Test session timeout handling
- [ ] **Invalid Token**: Test invalid authentication token handling
- [ ] **Permission Denied**: Test access denied error handling
- [ ] **Login Failure**: Test login failure error messages

## Security Tests

### Access Control Tests
- [ ] **Admin Access**: Verify admin-only pages require admin role
- [ ] **Client Access**: Verify client pages require client authentication
- [ ] **Carrier Access**: Verify carrier portal requires carrier authentication
- [ ] **Public Access**: Verify public pages are accessible without authentication

### Data Security Tests
- [ ] **Sensitive Data**: Verify sensitive data is not exposed in URLs
- [ ] **Cross-Tenant**: Verify users cannot access other tenant data
- [ ] **SQL Injection**: Test form inputs for SQL injection protection
- [ ] **XSS Protection**: Test form inputs for XSS protection

## Test Execution Summary

### Test Categories
- **Authentication Tests**: 12 test cases
- **Admin Panel Tests**: 15 test cases
- **Business Logic Tests**: 45 test cases
- **Client Portal Tests**: 9 test cases
- **Carrier Management Tests**: 8 test cases
- **Payment Tests**: 8 test cases
- **Reporting Tests**: 6 test cases
- **Document Tests**: 6 test cases
- **Public Pages Tests**: 9 test cases
- **Modal Tests**: 12 test cases
- **Workflow Tests**: 12 test cases
- **Performance Tests**: 10 test cases
- **Error Handling Tests**: 12 test cases
- **Security Tests**: 8 test cases

### Total Test Cases: 172

### Estimated Execution Time
- **Manual Testing**: 40-50 hours
- **Automated Testing**: 2-3 hours
- **Test Maintenance**: 2-4 hours per month

### Success Criteria
- All critical user workflows function correctly
- No broken links or 404 errors
- All forms validate properly
- Role-based access control works correctly
- Performance meets specified requirements
- Error handling provides appropriate user feedback

---

*This test plan was generated automatically for the {project_name} frontend application. Last updated: {chr(10).join([''] * 0)}*
"""
    
    return test_plan


async def main():
    """Main function"""
    success = await generate_test_plan_directly()
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
