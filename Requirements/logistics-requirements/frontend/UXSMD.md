---
document_type: UXSMD
generated_date: 2025-05-26T22:40:55.000000
generator: Claude Requirements Engine
version: 1.0
---

# UX Site-Map Requirements Document
**Transportation Management System (TMS) - Freight Brokerage Platform**

## Overview (UXSMD-1)

This document defines the complete user experience and site structure for the Transportation Management System, based on the analyzed freight brokerage load booking workflow. The frontend will be built using React/TypeScript with a focus on efficient load booking, carrier management, and operational workflows for freight brokers.

**Primary Users:** Freight brokers, operations managers, dispatchers
**Core Workflows:** Load booking, carrier selection, rate negotiation, document management

## Site Map (UXSMD-2)

### Primary Navigation Structure
```
Freight Brokerage TMS
├── Dashboard (/)
├── Operations (/operations)
│   ├── New Load Entry (/operations/new-load)
│   ├── Active Loads (/operations/active)
│   ├── Load History (/operations/history)
│   └── Load Templates (/operations/templates)
├── Carriers (/carriers)
│   ├── Carrier Search (/carriers/search)
│   ├── Carrier Database (/carriers/database)
│   ├── Onboarding (/carriers/onboarding)
│   └── Performance (/carriers/performance)
├── Customers (/customers)
│   ├── Customer Database (/customers/database)
│   ├── Rate Agreements (/customers/rates)
│   └── Customer Locations (/customers/locations)
├── Documents (/documents)
│   ├── Rate Confirmations (/documents/rate-cons)
│   ├── Bills of Lading (/documents/bol)
│   ├── Proof of Delivery (/documents/pod)
│   └── Rate Agreements (/documents/agreements)
└── Reports (/reports)
    ├── Margin Analysis (/reports/margins)
    ├── Carrier Performance (/reports/carriers)
    └── Load Statistics (/reports/loads)
```

## Page Specifications (UXSMD-3)

### Operations Dashboard
**Route:** `/`
**Purpose:** Central operations hub with key metrics and quick access to primary functions

**Layout Components:**
- Header with main navigation and user profile
- KPI cards (Active Loads, Daily Bookings, Margin %, Pending Rate Cons)
- Quick action buttons (New Load Entry, Carrier Search)
- Active loads grid with status indicators
- Recent activity feed
- Margin performance chart

**Key UI Elements:**
- "New Load Entry" prominent action button
- Load status indicators (Booked, In Transit, Delivered, Cancelled)
- Margin percentage with color coding (green >15%, yellow 10-15%, red <10%)
- Search bar for quick load/carrier lookup

### New Load Entry Wizard
**Route:** `/operations/new-load`
**Purpose:** Multi-step load booking interface

**Step 1: Load Configuration**
- Load type selection (Single Stop / Multi-Stop toggle)
- Trailer type dropdown (Flatbed, Dry Van, Reefer, etc.)
- Special equipment checkboxes (Tarps, Chains, etc.)
- Team driver requirement toggle

**Step 2: Customer Information**
- Customer search/selection (autocomplete dropdown)
- Team member assignment (editable for load credit)
- Payment terms (defaults to "Prepay")
- Customer reference numbers (Pickup #, Delivery #)

**Step 3: Location Details**
- Pickup location form with autocomplete
- Delivery location form with autocomplete
- New location creation modal
- Hours of operation time pickers
- Appointment vs FCFS selection
- Special instructions text areas

**Step 4: Cargo Specifications**
- Cargo description text field
- Weight input with unit selector (lbs/tons/kg)
- Estimated cargo value (required field with $ formatting)
- Dimensional inputs for oversize loads
- Hazmat classification (if applicable)

**Step 5: Documentation**
- Rate agreement upload interface
- Document preview capability
- File validation and storage
- Required document checklist

**Step 6: Carrier Selection**
- Carrier search interface (MC#, DOT#, Company Name)
- Carrier information display panel
- Available carriers list with performance scores
- Contact information and insurance status

**Step 7: Rate Negotiation**
- Customer rate input
- Carrier rate input
- Margin calculation display ($ amount and %)
- Rate confirmation preview
- Load validation checklist

### Carrier Search Interface
**Route:** `/carriers/search`
**Purpose:** Find and evaluate carriers for load assignments

**Layout Components:**
- Search criteria form (location, equipment, availability)
- Results grid with carrier details
- Carrier profile panels
- Performance metrics display
- Contact and communication tools

**Search Filters:**
- Geographic radius from pickup location
- Equipment type and availability
- Insurance coverage levels
- Performance ratings
- Recent activity status

### Dispatch Information Screen
**Route:** `/operations/dispatch/:loadId`
**Purpose:** Driver and equipment assignment for active loads

**Layout Components:**
- Load summary header
- Driver information form
- Equipment details (truck/trailer numbers)
- Contact information validation
- Load confirmation and rate con sending

**Validation Rules:**
- Phone number format: +1XXXXXXXXXX (no spaces)
- Required fields: Driver name, truck #, trailer #, phone
- Email validation for driver communication

## Navigation Flow (UXSMD-4)

### Primary User Journeys

**Journey 1: Book New Load**
1. Start: Dashboard → "New Load Entry" action button
2. Navigate: Multi-step load booking wizard
3. Actions: Configure → Customer → Locations → Cargo → Docs → Carrier → Rate
4. Result: Load booked → Rate confirmation sent → Return to dashboard

**Journey 2: Find Carrier for Load**
1. Start: Load entry wizard → Carrier selection step
2. Navigate: Carrier search interface
3. Actions: Search criteria → Review results → Select carrier
4. Result: Carrier assigned → Continue to rate negotiation

**Journey 3: Manage Active Load**
1. Start: Dashboard → Active loads grid → Select load
2. Navigate: Load detail page
3. Actions: Update status → Add notes → Send communications
4. Result: Load updated → Notifications sent

**Journey 4: Handle Load Cancellation**
1. Start: Active load detail page
2. Navigate: Cancellation workflow
3. Actions: Select reason → Mark for reuse → Notify parties
4. Result: Load cancelled → Available for rebooking

## User Journeys (UXSMD-5)

### Freight Broker Daily Workflow
**Persona:** Operations broker handling multiple loads daily
**Frequency:** Continuous throughout business hours

**Morning Routine:**
1. Check dashboard for overnight activity
2. Review pending rate confirmations
3. Follow up on loads requiring attention
4. Process new load requests from customers

**Load Booking Process:**
1. Receive load request from customer
2. Enter load details into booking system
3. Search for available carriers
4. Negotiate rates with carrier
5. Generate and send rate confirmation
6. Monitor load progress and communicate updates

**Exception Handling:**
- Carrier cancellations require immediate rebooking
- Customer changes require rate renegotiation
- Documentation issues need resolution before delivery

### Operations Manager Oversight Workflow
**Persona:** Supervisory role monitoring team performance
**Frequency:** Multiple times daily

**Steps:**
1. Review team performance metrics
2. Monitor margin percentages across loads
3. Identify carriers needing attention
4. Resolve escalated issues
5. Generate performance reports

## Wireframes (UXSMD-6)

### Load Booking Wizard - Step Layout
```
+-------------------------------------------------------+
| TMS Header Navigation                    | User Menu  |
+-------------------------------------------------------+
| Breadcrumb: Operations > New Load Entry > Step 2 of 7|
+-------------------------------------------------------+
| Progress Bar: [■■■■□□□] Customer Information         |
+-------------------------------------------------------+
| Customer Information                                  |
| Customer: [Search/Select Customer        ▼]         |
| Assigned To: [Kelly Pipe Team           ▼]         |
| Payment Terms: [Prepay                  ▼]         |
+-------------------------------------------------------+
| Reference Numbers                                     |
| Pickup Number: [1234                    ]           |
| Delivery Number: [4321                  ]           |
+-------------------------------------------------------+
| Customer Contact (Optional)                          |
| Contact Person: [                       ]           |
| Phone: [                                ]           |
+-------------------------------------------------------+
|                           [Back] [Next] [Save Draft] |
+-------------------------------------------------------+
```

### Carrier Search Results Layout
```
+-------------------------------------------------------+
| Search Criteria                                       |
| Location: [Within 100 miles of pickup] Equipment: [...] |
+-------------------------------------------------------+
| Results (24 carriers found)              | [Filters]  |
+-------------------------------------------------------+
| Carrier Name | MC# | Equipment | Rate | Score | Action|
|--------------|-----|-----------|------|-------|-------|
| ABC Transport| 123 | Flatbed   | $500 | 4.8★  |[Select]|
| XYZ Logistics| 456 | Flatbed   | $525 | 4.6★  |[Select]|
| Quick Haul   | 789 | Flatbed   | $480 | 4.9★  |[Select]|
+-------------------------------------------------------+
| Showing 1-10 of 24            | [Previous] [1][2] [Next] |
+-------------------------------------------------------+
```

### Rate Negotiation Interface
```
+-------------------------------------------------------+
| Load Summary: Pipe Transport - Hammond to Wichita    |
+-------------------------------------------------------+
| Pricing Information                                   |
| Customer Rate: [$1,100.00    ] (What we charge)     |
| Carrier Rate:  [$1,000.00    ] (What we pay)       |
+-------------------------------------------------------+
| Margin Analysis                                       |
| Margin Amount: $100.00                              |
| Margin Percentage: 9.09% ⚠️ (Below 10% threshold)  |
+-------------------------------------------------------+
| Rate Confirmation                                     |
| Carrier: ABC Transport (MC-123456)                  |
| Driver Email: [driver@abctransport.com]             |
| Special Instructions: [Standard pickup/delivery...  ] |
+-------------------------------------------------------+
|                    [Save Draft] [Send Rate Con] [Cancel] |
+-------------------------------------------------------+
```

## Responsive Design (UXSMD-7)

### Breakpoints
- Desktop: 1200px+ (Primary broker workstation layout)
- Tablet: 768px - 1199px (Mobile broker operations)
- Mobile: 320px - 767px (Emergency access and notifications)

### Mobile Adaptations
- Navigation collapses to hamburger menu
- Multi-step wizards become single-page scrollable forms
- Data grids convert to card-based layouts
- Quick action buttons remain prominent
- Search and filter controls optimize for touch

### Touch Interface Requirements
- Minimum touch target size: 44px
- Swipe gestures for navigation between wizard steps
- Pull-to-refresh for active loads
- Long-press context menus for quick actions

## Accessibility (UXSMD-8)

### WCAG 2.1 AA Compliance
- **Color Contrast:** 4.5:1 minimum for text
- **Keyboard Navigation:** Complete wizard navigation via keyboard
- **Screen Reader:** Proper labels for all form fields and actions
- **Focus Management:** Clear focus indicators throughout workflows

### Logistics-Specific Accessibility
- High contrast mode for warehouse/outdoor environments
- Large touch targets for mobile device usage
- Audio notifications for critical alerts
- Voice input capability for hands-free operation

## Technical Requirements (UXSMD-9)

### Frontend Technology Stack
- **Framework:** React 18+ with TypeScript
- **State Management:** Redux Toolkit for complex application state
- **UI Library:** Material-UI or Ant Design for consistent components
- **Forms:** React Hook Form with Yup validation
- **Maps Integration:** Google Maps API for location services
- **Real-time:** WebSocket connection for load status updates
- **File Upload:** Drag-and-drop with progress indicators

### Performance Requirements
- **Initial Load:** < 3 seconds on 3G connection
- **Wizard Navigation:** < 200ms between steps
- **Search Results:** < 1 second for carrier searches
- **Real-time Updates:** < 500ms for status changes
- **Offline Capability:** Draft loads saved locally

### Integration Requirements
- **API Communication:** RESTful API with proper error handling
- **Real-time Updates:** WebSocket for live load tracking
- **Document Viewing:** PDF rendering and annotation
- **Mapping Services:** Route optimization and mileage calculation
- **Communication:** Email/SMS integration for notifications

This UX Site-Map Requirements Document provides comprehensive frontend specifications for implementing the Transportation Management System, ensuring efficient freight brokerage operations through intuitive user interface design and optimized workflows.
