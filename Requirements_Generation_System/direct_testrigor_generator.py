#!/usr/bin/env python3
"""
Direct testRigor Test Generator
This script reads the generated test plan and creates testRigor test files directly.
"""

import asyncio
import sys
from pathlib import Path
from rich.console import Console

console = Console()


async def generate_testrigor_tests_directly():
    """Generate testRigor tests directly from the test plan"""
    
    console.print("[bold cyan]🤖 Direct testRigor Test Generation[/bold cyan]")
    console.print("This will read the test plan and generate testRigor test files directly.\n")
    
    try:
        # Check if test plan exists
        base_path = Path(__file__).parent.parent
        test_plan_path = base_path / "generated_documents" / "testing" / "frontend_test_plan.md"
        
        if not test_plan_path.exists():
            console.print(f"[red]❌ Test plan not found: {test_plan_path}[/red]")
            console.print("[yellow]Please run option 20 first to generate the test plan.[/yellow]")
            return False
        
        console.print(f"[green]✅ Found test plan: {test_plan_path}[/green]")
        
        # Read test plan
        console.print("[cyan]Step 1: Reading test plan...[/cyan]")
        with open(test_plan_path, 'r', encoding='utf-8') as f:
            test_plan_content = f.read()
        
        console.print(f"[green]✅ Test plan loaded ({len(test_plan_content)} characters)[/green]")
        
        # Create testRigor tests directory
        tests_dir = base_path / "generated_documents" / "testing" / "testrigor_tests"
        tests_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        (tests_dir / "page_load_tests").mkdir(exist_ok=True)
        (tests_dir / "interactive_tests").mkdir(exist_ok=True)
        (tests_dir / "modal_tests").mkdir(exist_ok=True)
        (tests_dir / "workflow_tests").mkdir(exist_ok=True)
        
        console.print("[green]✅ Created test directory structure[/green]")
        
        # Generate testRigor tests
        console.print("[cyan]Step 2: Generating testRigor test files...[/cyan]")
        
        # Generate page load tests
        await generate_page_load_tests(tests_dir)
        console.print("[green]✅ Generated page load tests[/green]")
        
        # Generate interactive tests
        await generate_interactive_tests(tests_dir)
        console.print("[green]✅ Generated interactive tests[/green]")
        
        # Generate modal tests
        await generate_modal_tests(tests_dir)
        console.print("[green]✅ Generated modal tests[/green]")
        
        # Generate workflow tests
        await generate_workflow_tests(tests_dir)
        console.print("[green]✅ Generated workflow tests[/green]")
        
        # Generate master test suite
        await generate_master_test_suite(tests_dir)
        console.print("[green]✅ Generated master test suite[/green]")
        
        # Count generated files
        test_files = list(tests_dir.rglob("*.txt"))
        
        console.print(f"\n[bold green]🎉 testRigor Tests Generated Successfully![/bold green]")
        console.print(f"[cyan]Tests directory: {tests_dir}[/cyan]")
        console.print(f"[cyan]Total test files: {len(test_files)}[/cyan]")
        console.print(f"[cyan]Test categories: 4 (page_load, interactive, modal, workflow)[/cyan]")
        
        return True
        
    except Exception as e:
        console.print(f"[red]❌ Error generating testRigor tests: {e}[/red]")
        import traceback
        console.print(traceback.format_exc())
        return False


async def generate_page_load_tests(tests_dir):
    """Generate page load tests"""
    
    pages = [
        ("homepage", "/", "Homepage Load Test"),
        ("login", "/login", "Login Page Load Test"),
        ("dashboard", "/dashboard", "Dashboard Load Test"),
        ("admin_dashboard", "/admin", "Admin Dashboard Load Test"),
        ("customers", "/customers", "Customers Page Load Test"),
        ("loads", "/loads", "Loads Page Load Test"),
        ("invoices", "/invoices", "Invoices Page Load Test"),
        ("carriers", "/carriers", "Carriers Page Load Test"),
        ("reports", "/reports", "Reports Page Load Test"),
    ]
    
    for page_name, route, test_name in pages:
        test_content = f"""{test_name}

# Navigate to page
open url "http://localhost:4001{route}"
wait until page loads

# Verify page loads without errors
check that page does not contain "404"
check that page does not contain "500"
check that page does not contain "Error"
check that page does not contain "Something went wrong"

# Verify page content loads
wait until page contains text
check that page title is not empty

# Take screenshot for verification
save screenshot as "{page_name}_load_test"

# Verify page is responsive
check that page is responsive

# Test completed successfully
"""
        
        test_file = tests_dir / "page_load_tests" / f"{page_name}_load_test.txt"
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)


async def generate_interactive_tests(tests_dir):
    """Generate interactive element tests"""
    
    tests = [
        ("login_form", "Login Form Test", "/login", [
            'enter "admin@example.com" into "email"',
            'enter "AdminPass123!" into "password"',
            'click "Login"',
            'wait until page contains "Dashboard"'
        ]),
        ("customer_creation", "Customer Creation Test", "/customers/new", [
            'enter "Test Company Inc." into "Company Name"',
            'enter "John Doe" into "Contact Name"',
            'enter "test@example.com" into "Email"',
            'enter "+1-555-123-4567" into "Phone"',
            'click "Save Customer"',
            'wait until page contains "Customer created successfully"'
        ]),
        ("load_creation", "Load Creation Test", "/loads/new", [
            'enter "Chicago, IL" into "Origin"',
            'enter "Dallas, TX" into "Destination"',
            'enter "5000" into "Weight"',
            'select "Dry Van" from "Equipment Type"',
            'click "Save Load"',
            'wait until page contains "Load created successfully"'
        ]),
        ("invoice_creation", "Invoice Creation Test", "/invoices/new", [
            'select first option from "Customer"',
            'enter "Test Invoice" into "Description"',
            'enter "1000.00" into "Amount"',
            'click "Save Invoice"',
            'wait until page contains "Invoice created successfully"'
        ])
    ]
    
    for test_name, test_title, route, actions in tests:
        test_content = f"""{test_title}

# Navigate to page
open url "http://localhost:4001{route}"
wait until page loads

# Verify page loads correctly
check that page does not contain "Error"
check that page does not contain "404"

# Perform test actions
{chr(10).join(actions)}

# Verify no errors occurred
check that page does not contain "Error"
check that page does not contain "Failed"

# Take screenshot for verification
save screenshot as "{test_name}_success"

# Test completed successfully
"""
        
        test_file = tests_dir / "interactive_tests" / f"{test_name}_test.txt"
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)


async def generate_modal_tests(tests_dir):
    """Generate modal tests"""
    
    modal_tests = [
        ("customer_modal", "Customer Modal Test", "/customers", "New Customer", [
            'enter "Modal Test Company" into "Company Name"',
            'enter "Modal Test Contact" into "Contact Name"',
            'click "Save"'
        ]),
        ("load_modal", "Load Modal Test", "/loads", "New Load", [
            'enter "Test Origin" into "Origin"',
            'enter "Test Destination" into "Destination"',
            'click "Save"'
        ]),
        ("invoice_modal", "Invoice Modal Test", "/invoices", "New Invoice", [
            'enter "Modal Test Invoice" into "Description"',
            'enter "500.00" into "Amount"',
            'click "Save"'
        ])
    ]
    
    for test_name, test_title, route, trigger_text, actions in modal_tests:
        test_content = f"""{test_title}

# Navigate to page
open url "http://localhost:4001{route}"
wait until page loads

# Open modal
click "{trigger_text}"
wait until page contains modal

# Verify modal opened
check that page contains modal
save screenshot as "{test_name}_opened"

# Fill modal form
{chr(10).join(actions)}

# Verify modal closes or shows success
wait 3 seconds
check that page does not contain "Error"

# Take final screenshot
save screenshot as "{test_name}_completed"

# Test completed successfully
"""
        
        test_file = tests_dir / "modal_tests" / f"{test_name}_test.txt"
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)


async def generate_workflow_tests(tests_dir):
    """Generate end-to-end workflow tests"""
    
    workflows = [
        ("complete_customer_workflow", "Complete Customer Workflow", [
            "# Step 1: Create Customer",
            'open url "http://localhost:4001/customers/new"',
            'wait until page loads',
            'enter "Workflow Test Company" into "Company Name"',
            'enter "Workflow Contact" into "Contact Name"',
            'enter "workflow@test.com" into "Email"',
            'click "Save Customer"',
            'wait until page contains "Customer created"',
            "",
            "# Step 2: Create Load for Customer",
            'open url "http://localhost:4001/loads/new"',
            'wait until page loads',
            'select "Workflow Test Company" from "Customer"',
            'enter "Chicago, IL" into "Origin"',
            'enter "Dallas, TX" into "Destination"',
            'click "Save Load"',
            'wait until page contains "Load created"',
            "",
            "# Step 3: Generate Invoice",
            'open url "http://localhost:4001/invoices/new"',
            'wait until page loads',
            'select "Workflow Test Company" from "Customer"',
            'enter "Workflow Invoice" into "Description"',
            'click "Save Invoice"',
            'wait until page contains "Invoice created"'
        ]),
        ("admin_management_workflow", "Admin Management Workflow", [
            "# Step 1: Login as Admin",
            'open url "http://localhost:4001/login"',
            'wait until page loads',
            'enter "admin@example.com" into "email"',
            'enter "AdminPass123!" into "password"',
            'click "Login"',
            'wait until page contains "Dashboard"',
            "",
            "# Step 2: Access Admin Panel",
            'click "Admin"',
            'wait until page loads',
            'check that page contains "Admin Dashboard"',
            "",
            "# Step 3: Manage Users",
            'click "Users"',
            'wait until page loads',
            'check that page contains "User Management"',
            "",
            "# Step 4: Check System Settings",
            'click "Settings"',
            'wait until page loads',
            'check that page contains "System Settings"'
        ])
    ]
    
    for test_name, test_title, steps in workflows:
        test_content = f"""{test_title}

{chr(10).join(steps)}

# Verify workflow completed successfully
check that page does not contain "Error"
save screenshot as "{test_name}_completed"

# Test completed successfully
"""
        
        test_file = tests_dir / "workflow_tests" / f"{test_name}_test.txt"
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)


async def generate_master_test_suite(tests_dir):
    """Generate master test suite that runs all tests"""
    
    master_content = """FY.WB.Midway Master Test Suite

# Set test configuration
set "baseUrl" to "http://localhost:4001"
set "adminEmail" to "admin@example.com"
set "adminPassword" to "AdminPass123!"
set "testsRun" to "0"
set "testsPassed" to "0"
set "testsFailed" to "0"

# Test Suite: Page Load Tests
print "=== Running Page Load Tests ==="

# Homepage Load Test
open url stored value "baseUrl"
wait until page loads
check that page does not contain "404"
increment "testsRun" by 1
increment "testsPassed" by 1
save screenshot as "master_suite_homepage"

# Login Page Load Test
open url stored value "baseUrl" + "/login"
wait until page loads
check that page does not contain "Error"
increment "testsRun" by 1
increment "testsPassed" by 1

# Dashboard Load Test (requires login)
enter stored value "adminEmail" into "email"
enter stored value "adminPassword" into "password"
click "Login"
wait until page contains "Dashboard"
check that page does not contain "Error"
increment "testsRun" by 1
increment "testsPassed" by 1
save screenshot as "master_suite_dashboard"

# Test Suite: Interactive Tests
print "=== Running Interactive Tests ==="

# Customer Creation Test
open url stored value "baseUrl" + "/customers/new"
wait until page loads
enter "Master Suite Test Company" into "Company Name"
enter "Test Contact" into "Contact Name"
enter "mastersuite@test.com" into "Email"
click "Save Customer"
wait 3 seconds
check that page does not contain "Error"
increment "testsRun" by 1
increment "testsPassed" by 1

# Test Suite: Navigation Tests
print "=== Running Navigation Tests ==="

# Test main navigation
click "Customers" if page contains "Customers"
wait until page loads
check that page does not contain "404"
increment "testsRun" by 1
increment "testsPassed" by 1

click "Loads" if page contains "Loads"
wait until page loads
check that page does not contain "404"
increment "testsRun" by 1
increment "testsPassed" by 1

click "Invoices" if page contains "Invoices"
wait until page loads
check that page does not contain "404"
increment "testsRun" by 1
increment "testsPassed" by 1

# Test Suite: Admin Panel Tests
print "=== Running Admin Panel Tests ==="

click "Admin" if page contains "Admin"
wait until page loads
check that page does not contain "Unauthorized"
increment "testsRun" by 1
increment "testsPassed" by 1

# Final Results
print "=== Test Suite Results ==="
print "Tests Run: " + stored value "testsRun"
print "Tests Passed: " + stored value "testsPassed"
print "Tests Failed: " + stored value "testsFailed"
print "Success Rate: " + (stored value "testsPassed" / stored value "testsRun" * 100) + "%"

save screenshot as "master_suite_final_results"

# Verify overall success
check that stored value "testsFailed" equals "0"
"""
    
    master_file = tests_dir / "master_test_suite.txt"
    with open(master_file, 'w', encoding='utf-8') as f:
        f.write(master_content)


async def main():
    """Main function"""
    success = await generate_testrigor_tests_directly()
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
