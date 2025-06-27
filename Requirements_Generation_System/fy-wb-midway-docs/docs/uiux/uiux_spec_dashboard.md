# Dashboard and Analytics Interface Design

This document defines the dashboard and analytics view specifications following the UXDMD format.

## View Catalogue

| View-ID | Title | Route | Upstream FRD | Primary API Endpoint(s) | User Roles |
|---------|-------|-------|--------------|-------------------------|------------|
| `view-dashboard-main` | Main Dashboard | `/dashboard` | FRD-3.1.3 | `GET /dashboard/metrics` | admin, user |
| `view-dashboard-reports` | Reports Dashboard | `/dashboard/reports` | FRD-3.3.2 | `GET /reports/financial` | admin, finance |

## Data Map

| Data Key | API Contract | Store Slice | Caching TTL | Loaded By (View-IDs) | Security |
|----------|--------------|-------------|-------------|---------------------|----------|
| `metrics` | `GET /dashboard/metrics` | `state.dashboard.metrics` | 30s | dashboard-main | auth required |
| `reports` | `GET /reports/financial` | `state.dashboard.reports` | 60s | dashboard-reports | finance role |

## Per-View Specification

### view-dashboard-main (UXDMD-1)

| Section | Detail |
|---------|--------|
| **Purpose** | Provide real-time overview of key business metrics and KPIs |
| **Layout** | Grid layout with metric cards, charts, and quick actions |
| **Displayed Fields** | Total Revenue • Active Loads • Customer Count • Payment Status |
| **Primary Actions** | Refresh Data • Export Report • View Details |
| **Secondary Actions** | Filter by date range, drill-down to specific metrics |
| **State Behavior** | Loading skeleton cards, empty state with onboarding |
| **API Mapping** | `GET /dashboard/metrics` (200/401/500) |
| **Error UX** | 401 → redirect to login, 500 → retry button with toast |
| **Security Notes** | Requires auth token, role-based metric visibility |
| **Analytics** | Track `dashboard.viewed`, `metric.clicked` events |
| **Accessibility** | ARIA labels for charts, keyboard navigation |
| **Design Tokens** | `--surface-elevated-1`, `--space-lg` |
| **Traceability Links** | FRD-3.1.3 • API-DASHBOARD-1 • NFRD-PERF-1 |

## Navigation

- [← Back to Master Document](./uiux_spec.md)
- [← Interaction Flows](./uiux_spec_interactions.md)
- [Customer Management →](./uiux_spec_customer_mgt.md)