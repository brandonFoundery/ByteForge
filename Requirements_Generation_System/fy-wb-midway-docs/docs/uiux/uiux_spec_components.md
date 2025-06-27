# Component Library and Design System Integration

This document defines the design system components and their integration patterns for the FY.WB.Midway platform.

## Design System Reference

**Primary Design System**: Material-UI v5 with custom theme
**Figma File**: [Design System v3.0](https://figma.com/design-system)
**Storybook**: [Component Library](https://storybook.fywbmidway.com)

## Component Specifications

### Form Components
| Component | Usage | API Binding | Validation |
|-----------|-------|-------------|------------|
| `CustomerForm` | Customer registration | POST /customers | Zod schema validation |
| `PaymentForm` | Payment processing | POST /payments | PCI DSS compliant |
| `LoadBookingForm` | Load booking | POST /loads | Business rule validation |

### Data Display Components
| Component | Usage | Data Source | Caching |
|-----------|-------|-------------|---------|
| `CustomerTable` | Customer listing | GET /customers | 60s TTL |
| `LoadTracker` | Real-time tracking | GET /loads/:id/track | 5s polling |
| `InvoiceList` | Invoice management | GET /invoices | 30s TTL |

### Layout Components
| Component | Usage | Responsive | Accessibility |
|-----------|-------|------------|---------------|
| `DashboardLayout` | Main layout | Mobile-first | ARIA landmarks |
| `FormLayout` | Form containers | Stacked on mobile | Focus management |
| `TableLayout` | Data tables | Horizontal scroll | Keyboard navigation |

## Design Tokens

### Color Palette
```css
--primary-50: #e3f2fd
--primary-500: #2196f3
--primary-900: #0d47a1
--secondary-500: #ff9800
--error-500: #f44336
--success-500: #4caf50

### Typography Scale
```css
--text-xs: 0.75rem
--text-sm: 0.875rem
--text-base: 1rem
--text-lg: 1.125rem
--text-xl: 1.25rem

### Spacing System
```css
--space-xs: 0.25rem
--space-sm: 0.5rem
--space-md: 1rem
--space-lg: 1.5rem
--space-xl: 2rem

## Component Variants

### Allowed Variants
- Button: primary, secondary, outline, text
- Input: standard, outlined, filled
- Card: elevated, outlined, filled

### Disallowed Variants
- Custom button styles outside design system
- Non-standard input decorations
- Inconsistent card shadows

## Theming and Customization

### Light/Dark Mode Support
- Automatic theme detection
- Manual theme toggle
- Persistent user preference
- System theme synchronization

### Responsive Behavior
- Mobile-first approach
- Breakpoints: 640px, 768px, 1024px, 1280px
- Fluid typography scaling
- Adaptive component layouts

## Navigation

- [← Back to Master Document](./uiux_spec.md)
- [← Information Architecture](./uiux_spec_architecture.md)
- [Interaction Flows →](./uiux_spec_interactions.md)