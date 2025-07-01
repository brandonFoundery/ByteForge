# Information Architecture and Navigation Design

This document defines the site structure, navigation patterns, and role-based access for the LSOMigrator platform.

## Site Map Structure

/
├── /dashboard (authenticated)
│   ├── /customers/list
│   └── /customers/new
│   ├── /loads/list
│   ├── /loads/book
│   ├── /carriers/register
│   └── /carriers/portal

## Navigation Patterns

### Primary Navigation
- Top navigation bar with role-based menu items
- Breadcrumb navigation for deep pages
- Quick action buttons for common tasks

### Role-Based Access
| Role | Accessible Routes | Permissions |
|------|------------------|-------------|
| Admin | All routes | Full CRUD access |
| Sales | /customers, /dashboard | Customer management |
| Finance | /payments, /invoices, /reports | Financial operations |
| Operations | /loads, /carriers | Logistics operations |

## Breadcrumb Rules
- Always show current location
- Include clickable parent levels
- Maximum 4 levels deep
- Home > Section > Subsection > Current Page

## Deep-Link Behavior
- All views support direct URL access
- State preserved in URL parameters
- Shareable URLs for filtered views
- Bookmark-friendly navigation

## Navigation

- [← Back to Master Document](./uiux_spec.md)
- [Component Library →](./uiux_spec_components.md)
- [Interaction Flows →](./uiux_spec_interactions.md)