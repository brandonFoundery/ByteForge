# Customer Management Interface Design

This document defines the customer management view specifications following the UXDMD format.

## View Catalogue

| View-ID | Title | Route | Upstream FRD | Primary API Endpoint(s) | User Roles |
|---------|-------|-------|--------------|-------------------------|------------|
| `view-customer-list` | Customer List | `/customers` | FRD-3.1.1 | `GET /customers` | admin, sales |
| `view-customer-detail` | Customer Detail | `/customers/:id` | FRD-3.1.1 | `GET /customers/{id}` | admin, sales |
| `view-customer-onboard` | Customer Onboarding | `/customers/new` | FRD-3.1.1 | `POST /customers` | admin, sales |

## Data Map

| Data Key | API Contract | Store Slice | Caching TTL | Loaded By (View-IDs) | Security |
|----------|--------------|-------------|-------------|---------------------|----------|
| `customers` | `GET /customers` | `state.customers.list` | 60s | customer-list | auth required |
| `customer` | `GET /customers/{id}` | `state.customers.byId[id]` | 15s | customer-detail | auth required |

## Per-View Specification

### view-customer-list (UXDMD-2)

| Section | Detail |
|---------|--------|
| **Purpose** | Display paginated list of customers with search and filtering |
| **Layout** | Data table with filters sidebar and action toolbar |
| **Displayed Fields** | Name • Email • Account Type • Status • Created Date • Actions |
| **Primary Actions** | Add Customer → `/customers/new`, View Details → `/customers/:id` |
| **Secondary Actions** | Export CSV, bulk actions, column sorting |
| **State Behavior** | Loading skeleton rows, empty state with CTA |
| **API Mapping** | `GET /customers?page={n}&search={q}` (200/401/500) |
| **Error UX** | Network errors show retry toast, empty results show help text |
| **Security Notes** | Role-based column visibility, data filtering by permissions |
| **Analytics** | Track `customer.list.viewed`, `customer.search` events |
| **Accessibility** | Table headers, row selection, keyboard navigation |
| **Design Tokens** | `--surface-base`, `--space-md` |
| **Traceability Links** | FRD-3.1.1 • API-CUSTOMERS-1 • NFRD-A11Y-1 |

### view-customer-detail (UXDMD-3)

| Section | Detail |
|---------|--------|
| **Purpose** | Display and edit detailed customer information |
| **Layout** | Card-based layout with tabs for different data sections |
| **Displayed Fields** | Profile Info • Contact Details • Payment History • Load History |
| **Primary Actions** | Edit Customer, View Loads, Process Payment |
| **Secondary Actions** | Export data, send communication, archive customer |
| **State Behavior** | Loading states for each tab, optimistic updates |
| **API Mapping** | `GET /customers/{id}`, `PATCH /customers/{id}` |
| **Error UX** | Validation errors inline, save conflicts with merge UI |
| **Security Notes** | Field-level permissions, audit trail for changes |
| **Analytics** | Track `customer.detail.viewed`, `customer.edited` events |
| **Accessibility** | Tab navigation, form labels, error announcements |
| **Design Tokens** | `--surface-elevated-2`, `--space-lg` |
| **Traceability Links** | FRD-3.1.1 • API-CUSTOMERS-2 • NFRD-SEC-2 |

## Navigation

- [← Back to Master Document](./uiux_spec.md)
- [← Dashboard Views](./uiux_spec_dashboard.md)
- [Payment Processing →](./uiux_spec_payment_proc.md)