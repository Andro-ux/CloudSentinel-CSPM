# CloudSentinel Frontend Theme

## Design Philosophy

The CloudSentinel frontend uses a **retro game theme** inspired by classic arcade games, terminal interfaces, and cyberpunk aesthetics. This distinguishes it from generic AI-generated SaaS themes and creates a memorable, cohesive identity.

## Color System

### Primary Colors

| Role | Color | Hex | Usage |
|------|-------|-----|-------|
| Primary | Neon Green | `#00ff9d` | Buttons, links, active states |
| Primary Dim | Green | `#00cc7d` | Hover states |
| Secondary | Magenta | `#ff00ff` | Accents, highlights |
| Accent | Cyan | `#00ffff` | Focus rings, secondary actions |

### Surface Colors

| Role | Color | Hex | Usage |
|------|-------|-----|-------|
| Background | Dark Purple | `#0f0f1b` | Main background |
| Surface | Purple | `#1a1a2e` | Cards, panels |
| Surface Alt | Lighter Purple | `#252542` | Inputs, hover states |
| Border | Muted Purple | `#3a3a5c` | Borders, dividers |

### Text Colors

| Role | Color | Hex | Usage |
|------|-------|-----|-------|
| Text | Light Lavender | `#e0e0ff` | Primary text |
| Text Muted | Muted Lavender | `#8888aa` | Secondary text, labels |

### Risk Level Colors

| Level | Color | Hex | Usage |
|-------|-------|-----|-------|
| Critical | Red | `#ff0040` | Critical risks, errors |
| High | Orange | `#ff6600` | High risks, warnings |
| Medium | Yellow | `#ffcc00` | Medium risks, alerts |
| Low | Blue | `#00ccff` | Low risks, info |
| Healthy | Green | `#00ff9d` | Healthy status, success |

## Typography

### Font Families

- **Retro**: `Press Start 2P` - Headings, labels, branding
- **Mono**: `Fira Code` - Data, code, metrics
- **Sans**: `Inter` - Body text, UI elements

### Font Usage

```tsx
// Retro font for headings
<h1 className="font-retro">CLOUDSENTINEL</h1>

// Mono font for data
<span className="font-mono">42</span>

// Sans for body
<p className="font-sans">Description text</p>
```

## Shadows

Retro game shadows use solid offsets rather than blur:

```css
/* Standard retro shadow */
box-shadow: 4px 4px 0px 0px rgba(0, 255, 157, 0.3);

/* Small retro shadow */
box-shadow: 2px 2px 0px 0px rgba(0, 255, 157, 0.2);

/* Glow effect */
box-shadow: 0 0 20px rgba(0, 255, 157, 0.3);
```

## Animations

### Pulse

```css
animation: pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite;
```

### Scanline

```css
.retro-card::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 100%;
  background: linear-gradient(
    transparent 50%,
    rgba(0, 0, 0, 0.1) 50%
  );
  background-size: 100% 4px;
  pointer-events: none;
  opacity: 0.3;
}
```

## Components

### Retro Card

```tsx
<div className="retro-card">
  {/* Card content */}
</div>
```

Features:
- Dark surface background
- Retro shadow
- Optional hover effect
- Optional scanline overlay

### Retro Button

```tsx
<Button variant="retro">CLICK ME</Button>
```

Features:
- Neon green background
- Retro shadow
- Press animation (shadow reduces on click)

### Retro Input

```tsx
<Input variant="retro" placeholder="Enter text" />
```

Features:
- Dark background
- Mono font
- Focus ring with glow
- Retro border

## Theme Support

The theme system supports three modes:

1. **Dark** (default): Full retro game theme
2. **Light**: Light variant with adjusted colors
3. **System**: Follows OS preference

```tsx
const { theme, setTheme, resolvedTheme } = useTheme()
```

## Accessibility

- High contrast ratios (WCAG AA)
- Focus indicators on all interactive elements
- Keyboard navigation support
- Screen reader friendly labels
- No reliance on color alone for meaning

## Responsive Design

- Mobile-first approach
- Collapsible sidebar on small screens
- Responsive grid layouts
- Touch-friendly tap targets
- Flexible typography scaling
