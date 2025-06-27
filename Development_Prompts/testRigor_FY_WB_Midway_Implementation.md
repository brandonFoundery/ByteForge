# testRigor Implementation for FY.WB.Midway

## 🎯 Ready-to-Use Prompt for FY.WB.Midway Project

This is the customized prompt specifically configured for the FY.WB.Midway Enterprise Logistics Platform.

---

### System Prompt
```
You are an expert QA automation engineer specializing in testRigor natural-language DSL. You create comprehensive, maintenance-free test scripts that systematically validate entire SaaS applications without requiring manual locator updates.
```

### User Prompt - FY.WB.Midway Specific
```
**Context & Configuration**

* **Base URL**: `http://localhost:4000`
* **Backend API**: `http://localhost:5002`
* **Authentication**: 
  - Login Path: `/login`
  - Admin: `admin@example.com` / `AdminPass123!`
  - Tenant User: `alex.rodriguez@techcorp.com` / `Test123!`
* **Domain Scope**: Only test internal links within `localhost:4000`
* **Destructive Actions**: Skip elements containing "delete", "remove", "reset", "purge", "clear all"
* **Special Pages**: Skip external integrations, payment gateways, and third-party redirects

**Application Architecture**
* **Frontend**: Next.js with TypeScript, Tailwind CSS
* **Backend**: ASP.NET Core with JWT authentication
* **Database**: Azure SQL with Entity Framework
* **Multi-tenant**: Role-based access (Admin, Tenant User, Carrier)

**Known Application Routes**
```
Public Routes:
- / (landing page)
- /login
- /register
- /public/about
- /public/contact

Authenticated Routes:
- /dashboard (main dashboard)
- /admin/index (admin dashboard)
- /admin/settings (system settings)
- /admin/tenants (tenant management)
- /admin/users (user management)
- /client/index (client dashboard)
- /client/profile (client profile)
- /client/settings (client settings)
- /customers/index (customer list)
- /customers/new (new customer)
- /customers/[id] (customer details)
- /loads/index (load list)
- /loads/new (new load)
- /loads/[id] (load details)
- /invoices/index (invoice list)
- /invoices/new (new invoice)
- /invoices/[id] (invoice details)
- /carriers/index (carrier list)
- /carriers/register (carrier registration)
- /carrier/portal (carrier portal)
- /payments/index (payment management)
- /payouts/index (payout management)
- /reports/index (reporting dashboard)
- /documents/index (document management)
- /tenant (tenant selection)
```

**Task Requirements**

Generate a single **testRigor test case** called **"FY.WB.Midway Full-Site Smoke Test"** that:

1. **Authentication Flow**:
   - Open `http://localhost:4000`
   - If redirected to login, enter `admin@example.com` and `AdminPass123!`
   - Click "Login" or "Sign In" button
   - Verify successful login by checking for "Dashboard" or "Welcome" text
   - Store authentication state for session

2. **Admin Role Testing**:
   - Navigate to `/dashboard` and verify page loads
   - Test admin-specific routes:
     * `/admin/index` - verify admin dashboard
     * `/admin/settings` - check system settings
     * `/admin/tenants` - test tenant management
     * `/admin/users` - verify user management
   - Click all navigation menu items
   - Test CRUD operations where forms are present

3. **Core Business Logic Testing**:
   - **Customer Management**:
     * Visit `/customers/index`
     * Click "New Customer" or "Add Customer" if present
     * Fill customer form with test data
     * Save and verify customer appears in list
   - **Load Management**:
     * Visit `/loads/index`
     * Test load creation workflow
     * Verify load tracking functionality
   - **Invoice Management**:
     * Visit `/invoices/index`
     * Test invoice generation
     * Verify invoice details view

4. **Multi-Role Testing**:
   - Logout from admin account
   - Login as tenant user: `alex.rodriguez@techcorp.com` / `Test123!`
   - Verify restricted access (admin routes should be blocked)
   - Test tenant-specific functionality:
     * `/client/index`
     * `/client/profile`
     * `/client/settings`

5. **Interactive Element Testing**:
   - Click every visible button, link, and interactive element
   - Fill forms with valid test data:
     * Company names: "Test Company Inc."
     * Contact names: "John Doe"
     * Email fields: "test@example.com"
     * Phone fields: "+1-555-123-4567"
     * Addresses: "123 Test Street, Test City, TS 12345"
     * Dates: Current date + 30 days
     * Dropdowns: Select first available option
   - Submit forms and verify no errors

6. **Error Detection & Validation**:
   - After each action, verify page does not contain:
     * "404", "500", "Error", "Exception"
     * "Unauthorized", "Access Denied"
     * "Something went wrong"
     * "Internal Server Error"
   - Verify successful navigation (URL changes appropriately)
   - Check for loading states completion

7. **Data Integrity Checks**:
   - Verify CRUD operations don't break navigation
   - Check that created test data appears in lists
   - Ensure pagination works if present
   - Validate search functionality if available

8. **Session Management**:
   - Test logout functionality
   - Verify session timeout handling
   - Check role-based access restrictions

**Technical Implementation Requirements**

- Use testRigor's natural language commands exclusively
- Implement robust wait strategies: `wait until page contains "Dashboard"` or `wait 3 seconds`
- Use loops for dynamic content: `click "Next" until page does not contain "Next"`
- Store page titles and URLs in variables for reporting
- Take screenshots at key checkpoints: `save screenshot as "admin-dashboard"`
- Handle modals and popups: `if page contains "modal" then click "Close"`
- Implement error recovery: `if page contains "Error" then go back`

**Output Format**

Provide the complete testRigor script in plain text format (no markdown formatting). Include:
- Clear step numbering and comments
- Variable declarations for reusable data
- Conditional logic for different user roles
- Comprehensive error handling
- Final summary report with statistics

**Success Criteria**

The generated script should:
- Execute without manual intervention
- Test both admin and tenant user roles
- Cover all major logistics workflows
- Provide clear pass/fail results
- Complete execution in under 20 minutes
- Achieve 85%+ page coverage for authenticated users
```

---

## 🚀 Quick Start Instructions

1. **Copy the prompt above**
2. **Paste into GPT-4 or Claude**
3. **Review the generated testRigor script**
4. **Create new test case in testRigor platform**
5. **Paste the generated script**
6. **Set environment variables**:
   - `BASE_URL`: `http://localhost:4000`
   - `ADMIN_EMAIL`: `admin@example.com`
   - `ADMIN_PASSWORD`: `AdminPass123!`
   - `TENANT_EMAIL`: `alex.rodriguez@techcorp.com`
   - `TENANT_PASSWORD`: `Test123!`
7. **Execute the test**

---

## 📋 Pre-Execution Checklist

- [ ] Frontend server running on `http://localhost:4000`
- [ ] Backend API running on `http://localhost:5002`
- [ ] Database seeded with test users
- [ ] Admin account accessible
- [ ] Tenant account accessible
- [ ] No blocking popups or maintenance modes

---

## 🔍 Expected Test Coverage

**Pages Tested**: 20+ routes
**User Roles**: Admin, Tenant User
**Core Workflows**: Customer, Load, Invoice, Carrier Management
**Forms**: Registration, Profile, Business Logic Forms
**Navigation**: All menu items and breadcrumbs
**Error Handling**: 404, 500, Unauthorized scenarios

---

## 📊 Success Metrics

- **Page Coverage**: 85%+ of authenticated routes
- **Error Detection**: 100% of broken links/forms
- **Execution Time**: < 20 minutes
- **False Positives**: < 5%
- **Maintenance**: Minimal (testRigor AI handles locator changes)

---

## 🛠️ Troubleshooting

**Common Issues**:
- **Login fails**: Check credentials and backend connectivity
- **Pages timeout**: Increase wait times for slow loading
- **Elements not found**: Verify UI hasn't changed significantly
- **Role restrictions**: Ensure test users have correct permissions

**Debug Steps**:
1. Run test in debug mode
2. Check screenshots at failure points
3. Verify backend logs for API errors
4. Confirm database state
5. Test manually to isolate issues
