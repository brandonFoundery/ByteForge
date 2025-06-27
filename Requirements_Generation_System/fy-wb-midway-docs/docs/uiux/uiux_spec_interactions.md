# Interaction Flows and User Journeys

This document defines the interaction patterns, user flows, and state management for the FY.WB.Midway platform.

## Primary User Flows

### Customer Onboarding Flow
```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant A as API
    participant D as Database

    U->>F: Navigate to /customers/new
    F->>F: Render CustomerForm
    U->>F: Fill form and submit
    F->>A: POST /customers
    A->>D: Validate and store
    D->>A: Return customer ID
    A->>F: 201 Created response
    F->>F: Navigate to /customers/:id
    F->>U: Show success message

### Payment Processing Flow
```mermaid
stateDiagram-v2
    [*] --> FormEntry
    FormEntry --> Validating: Submit
    Validating --> Processing: Valid
    Validating --> FormEntry: Invalid
    Processing --> Success: Approved
    Processing --> Failed: Declined
    Success --> [*]
    Failed --> FormEntry: Retry

### Load Tracking Flow
```mermaid
journey
    title Load Tracking User Journey
    section Booking
      Book Load: 5: Customer
      Receive Confirmation: 4: Customer
    section Tracking
      Check Status: 3: Customer
      View Location: 4: Customer
      Get Updates: 5: Customer
    section Delivery
      Confirm Delivery: 5: Customer
      Rate Service: 3: Customer

## State Management Patterns

### Global State Structure
```typescript
interface AppState {
  auth: AuthState;
  customers: CustomersState;
  loads: LoadsState;
  payments: PaymentsState;
  invoices: InvoicesState;
  carriers: CarriersState;
  ui: UIState;
}

### Component State Patterns
| Pattern | Usage | Example |
|---------|-------|---------|
| Local State | Form inputs, UI toggles | `useState` for form fields |
| Global State | User data, app settings | Redux/Zustand for auth |
| Server State | API data, caching | React Query for API calls |
| URL State | Filters, pagination | URL params for table state |

## Error Handling Flows

### Form Validation Errors
1. Client-side validation on blur/submit
2. Display field-level error messages
3. Prevent submission until resolved
4. Focus first error field

### API Error Handling
1. Network errors → Retry mechanism
2. 4xx errors → User-friendly messages
3. 5xx errors → Generic error page
4. Timeout errors → Retry with backoff

### Recovery Patterns
- Auto-save for long forms
- Optimistic updates with rollback
- Offline queue for critical actions
- Session recovery after auth expiry

## Animation and Transitions

### Micro-interactions
- Button hover states (150ms ease)
- Form field focus (200ms ease-in-out)
- Loading spinners (infinite rotation)
- Success checkmarks (300ms bounce)

### Page Transitions
- Route changes (250ms slide)
- Modal open/close (200ms fade + scale)
- Drawer slide (300ms ease-out)
- Tab switching (150ms fade)

### Performance Guidelines
- Animations under 300ms
- Use transform/opacity for performance
- Respect prefers-reduced-motion
- Hardware acceleration for smooth 60fps

## Navigation

- [← Back to Master Document](./uiux_spec.md)
- [← Component Library](./uiux_spec_components.md)
- [Dashboard Views →](./uiux_spec_dashboard.md)