# Dify Design System Specification (v1.11.4)

## Deep Analysis — Requirements Document

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Design Tokens](#2-design-tokens)
3. [Component Inventory](#3-component-inventory)
4. [Form System](#4-form-system)
5. [Modal/Dialog System](#5-modaldialog-system)
6. [Toast/Notification System](#6-toastnotification-system)
7. [Loading States](#7-loading-states)
8. [Icon System](#8-icon-system)
9. [Dark Mode](#9-dark-mode)
10. [Responsive Design](#10-responsive-design)
11. [Animation & Transitions](#11-animation--transitions)
12. [Accessibility](#12-accessibility)
13. [Patterns & Conventions](#13-patterns--conventions)

---

## 1. Architecture Overview

### Technology Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| Framework | Next.js | 15.x |
| Styling | Tailwind CSS | 3.x |
| Variant Management | class-variance-authority (CVA) | — |
| Headless Components | @headlessui/react | 2.2.1 |
| Floating UI | @floating-ui/react | — |
| Icons | @remixicon/react | 4.7.0 |
| Theme Management | next-themes | 0.4.6 |
| Testing | Vitest + @testing-library/react | 16.3.0 |

### File Structure

```
web/
├── tailwind.config.js              # Main config (imports tailwind-common-config)
├── tailwind-common-config.ts       # Extended tokens, colors, shadows, screens
├── postcss.config.js               # tailwindcss + autoprefixer
├── typography.js                   # @tailwindcss/typography prose config
├── themes/
│   ├── light.css                   # 765+ CSS variables (html[data-theme="light"])
│   ├── dark.css                    # 765+ CSS variables (html[data-theme="dark"])
│   └── tailwind-theme-var-define.ts # Maps CSS vars → Tailwind utilities
├── app/
│   ├── styles/
│   │   ├── globals.css             # Utility classes, border-radius scale, typography scale
│   │   ├── preflight.css           # Custom reset (Tailwind preflight disabled)
│   │   ├── markdown.scss           # Markdown rendering styles
│   │   └── monaco-sticky-fix.css   # Monaco editor dark mode fix
│   └── components/base/            # 101 component directories
└── hooks/use-theme.ts              # Theme hook wrapping next-themes
```

### Design Philosophy

- **Token-first**: All visual properties driven by CSS custom properties
- **Auto-generated tokens**: Theme CSS files are code-generated (likely from Figma)
- **Semantic naming**: Tokens named by purpose, not value (`text-text-primary`, not `text-gray-900`)
- **CVA for variants**: Type-safe variant management on base components
- **Headless UI for behavior**: Accessible interaction patterns from @headlessui/react
- **No runtime JS theming**: CSS variables swap via `data-theme` attribute

---

## 2. Design Tokens

### 2.1 Color System

#### Static Palette (tailwind-common-config.ts)

**Gray Scale:**

| Token | Hex |
|-------|-----|
| gray-25 | #fcfcfd |
| gray-50 | #f9fafb |
| gray-100 | #f2f4f7 |
| gray-200 | #eaecf0 |
| gray-300 | #d0d5dd |
| gray-400 | #98a2b3 |
| gray-500 | #667085 |
| gray-600 | #344054 |
| gray-700 | #475467 |
| gray-800 | #1d2939 |
| gray-900 | #101828 |

**Primary (Blue) Scale:**

| Token | Hex |
|-------|-----|
| primary-25 | #f5f8ff |
| primary-50 | #eff4ff |
| primary-100 | #d1e0ff |
| primary-200 | #b2ccff |
| primary-300 | #84adff |
| primary-400 | #528bff |
| primary-500 | #2970ff |
| primary-600 | #155eef |
| primary-700 | #004eeb |
| primary-800 | #0040c1 |
| primary-900 | #00359e |

**Additional scales**: Indigo (25–800), Green, Yellow, Purple, Blue.

#### Semantic Color Tokens (765+ CSS variables)

Organized by category in `themes/light.css` and `themes/dark.css`:

**Text Colors (21 tokens):**
- `--color-text-primary` — Main body text
- `--color-text-secondary` — Supporting text
- `--color-text-tertiary` — De-emphasized text
- `--color-text-quaternary` — Weakest text
- `--color-text-destructive` — Error/danger text
- `--color-text-success` — Success text
- `--color-text-warning` — Warning text
- `--color-text-accent` — Brand accent text
- `--color-text-accent-secondary` — Secondary accent
- `--color-text-placeholder` — Placeholder text
- `--color-text-disabled` — Disabled text
- `--color-text-primary-on-surface` — Text on colored surface
- `--color-text-inverted` — Text on dark background
- `--color-text-logo-text` — Logo text
- `--color-text-empty-state-icon` — Empty state icon color

**Background Colors (22+ tokens):**
- `--color-bg-body` — Page body
- `--color-bg-default` — Default card/container
- `--color-bg-soft` — Soft background
- `--color-bg-default-hover` — Hover state
- `--color-bg-default-dimmed` — Dimmed background
- `--color-bg-section` — Section background
- `--color-bg-overlay-*` — Overlays (fullscreen, backdrop, alt, destructive)
- `--color-bg-surface-white` — White surface

**Component Colors (385+ tokens):**
Namespaced per component:
- `--color-components-input-*` — Input fields (bg-normal, bg-hover, bg-active, border-*, text-*)
- `--color-components-button-*` — Buttons (primary/secondary/tertiary/ghost/destructive × text/bg/border/disabled/hover)
- `--color-components-checkbox-*` — Checkbox (icon, bg, border, disabled)
- `--color-components-toggle-*` — Toggle (knob, bg)
- `--color-components-radio-*` — Radio (icon, bg, border, disabled)
- `--color-components-card-*` — Card (bg, border, bg-alt)
- `--color-components-panel-*` — Panel (bg, border, gradient, blur)
- `--color-components-slider-*` — Slider (knob, range, track, border)
- `--color-components-badge-*` — Badge (5+ status types)
- `--color-components-segmented-control-*` — Segmented control
- `--color-components-option-card-*` — Option card (bg, border, selected, hover)
- `--color-components-tab-*` — Tab (active color)
- `--color-components-chart-*` — Chart (line, area, bg)
- `--color-components-action-bar-*` — Action bar (bg, border)
- `--color-components-dropzone-*` — Dropzone (bg, border)
- `--color-components-progress-*` — Progress (brand/white/gray/warning/error)
- `--color-components-chat-input-*` — Chat input (audio, wave, masks)
- `--color-components-avatar-*` — Avatar (shape fills, mask)
- `--color-components-premium-badge-*` — Premium badge (4 color schemes)
- `--color-components-progress-bar-*` — Progress bar (bg, progress, border, highlight)
- `--color-components-main-nav-*` — Main nav (button text/bg, user border)
- `--color-components-menu-item-*` — Menu item (text, bg active/hover)
- `--color-components-tooltip-*` — Tooltip (bg)
- `--color-components-kbd-*` — Kbd (bg-gray, bg-white)

**State Colors (21 tokens):**
- `--color-state-base-hover`, `--color-state-base-active`
- `--color-state-accent-hover`, `--color-state-accent-active`, `--color-state-accent-solid`
- `--color-state-destructive-hover`, `--color-state-destructive-active`, `--color-state-destructive-solid`
- `--color-state-success-*`, `--color-state-warning-*`

**Divider Colors (8 tokens):**
- subtle, regular, deep, burn, intense, solid, solid-alt, accent

**Shadow Colors (10 tokens):**
- `--color-shadow-shadow-1` through `--color-shadow-shadow-10`

**Workflow Colors (60+ tokens):**
- Block, canvas, link-line, minimap, display states, workflow-progress

**Utility Color Scales (140+ tokens):**
Extended 8-shade palettes: Orange, Pink, Fuchsia, Purple, Indigo, Blue, Teal, Cyan, Violet, Red, Green, Yellow, Rose, Midnight, Gray-blue, Blue-light, Green-light, Orange-dark, Blue-brand.

**Icon Background Tokens (22 tokens):**
- Solid + soft variants for: Red, Rose, Pink, Orange, Yellow, Green, Teal, Blue, Indigo, Violet, Midnight

**Third-Party Colors:**
- LangChain, Langfuse, GitHub, OpenAI, Anthropic, AWS, Dify brand

### 2.2 Typography

#### Font Families
- **System**: Default Tailwind sans-serif stack
- **Instrument**: `var(--font-instrument-serif)`, serif (decorative/display)

#### Type Scale (globals.css utility classes)

**System Text** — 14 sizes × 3 weights:

| Class Pattern | Size | Line Height | Weight |
|---------------|------|-------------|--------|
| `system-2xs-*` | 0.625rem (10px) | — | regular / medium / semibold |
| `system-xs-*` | 0.75rem (12px) | — | regular / medium / semibold |
| `system-sm-*` | 0.875rem (14px) | — | regular / medium / semibold |
| `system-md-*` | 1rem (16px) | — | regular / medium / semibold |
| `system-lg-*` | 1.125rem (18px) | — | regular / medium / semibold |
| `system-xl-*` | 1.25rem (20px) | — | regular / medium / semibold |

Additional variant: `system-md-semibold-uppercase`

**Code Text** — 3 sizes × 2 weights:

| Class Pattern | Sizes |
|---------------|-------|
| `code-{xs,sm,md}-{regular,semibold}` | xs, sm, md |

**Body Text** — 5 sizes × 3 weights:

| Class Pattern | Sizes |
|---------------|-------|
| `body-{xs,sm,md,lg,2xl}-{light,regular,medium}` | xs → 2xl |

**Title Text** — 7 sizes × 2 weights:

| Class Pattern | Sizes |
|---------------|-------|
| `title-{xs,sm,md,lg,2xl,4xl,8xl}-{semi-bold,bold}` | xs → 8xl |

### 2.3 Border Radius Scale

| Token | Value |
|-------|-------|
| radius-2xs | 2px |
| radius-xs | 4px |
| radius-sm | 6px |
| radius-md | 8px |
| radius-lg | 10px |
| radius-xl | 12px |
| radius-2xl | 16px |
| radius-3xl | 20px |
| radius-4xl | 24px |
| radius-full | 64px |

### 2.4 Box Shadows

| Token | Value |
|-------|-------|
| xs | `0px 1px 2px 0px rgba(16,24,40,0.05)` |
| sm | `0px 1px 2px 0px rgba(16,24,40,0.06), 0px 1px 3px 0px rgba(16,24,40,0.10)` |
| md | Progressive elevation |
| lg | Progressive elevation |
| xl | Progressive elevation |
| 2xl | Progressive elevation |
| 3xl | Progressive elevation |

**Status shadows**: green, warning, red, blue, gray variants.

### 2.5 Breakpoints

| Token | Value | Usage |
|-------|-------|-------|
| mobile | 100px | Minimum viewport |
| tablet | 640px | Tablet portrait |
| pc | 769px | Desktop |
| 2k | 2560px | High-res desktop |
| sm (Tailwind) | 640px | Also used |
| md (Tailwind) | 768px | Also used |
| lg (Tailwind) | 1024px | Also used |
| xl (Tailwind) | 1280px | Also used |

### 2.6 Opacity

| Token | Value |
|-------|-------|
| 2 | 0.02 |
| 8 | 0.08 |

### 2.7 Animations

| Token | Value |
|-------|-------|
| spin-slow | `spin 2s linear infinite` |

---

## 3. Component Inventory

### 3.1 Full Component List (101 directories)

```
action-button          agent-log-modal        amplitude
answer-icon            app-icon               app-icon-picker
audio-btn              audio-gallery          auto-height-textarea
avatar                 badge                  block-input
button                 chat                   checkbox
checkbox-list          chip                   confirm
content-dialog         copy-feedback          copy-icon
corner-label           date-and-time-picker   dialog
divider                drawer                 drawer-plus
dropdown               effect                 emoji-picker
encrypted-bottom       error-boundary         features
file-icon              file-thumb             file-uploader
float-right-container  form                   fullscreen-modal
ga                     grid-mask              icons
image-gallery          image-uploader         inline-delete-confirm
input                  input-number           input-with-copy
linked-apps-panel      list-empty             loading
logo                   markdown               markdown-blocks
mermaid                message-log-modal      modal
modal-like-wrap        new-audio-button       node-status
notion-connector       notion-icon            notion-page-selector
pagination             param-item             popover
portal-to-follow-elem  premium-badge          progress-bar
prompt-editor          prompt-log-modal       qrcode
radio                  radio-card             search-input
segmented-control      select                 simple-pie-chart
skeleton               slider                 sort
spinner                svg                    svg-gallery
switch                 tab-header             tab-slider
tab-slider-new         tab-slider-plain       tag
tag-input              tag-management         text-generation
textarea               timezone-label         toast
tooltip                video-gallery          voice-input
with-input-validation  zendesk
```

### 3.2 Components Using CVA (12)

| Component | Variants | Sizes |
|-----------|----------|-------|
| **Button** | primary, warning, secondary, secondary-accent, ghost, ghost-accent, tertiary | small, medium, large |
| **Input** | — | regular, large |
| **Textarea** | — | small, regular, large |
| **Badge** | Warning, Accent, Default (state enum) | s, m, l |
| **Divider** | horizontal/vertical; gradient/solid | — |
| **ActionButton** | Destructive, Active, Disabled, Default, Hover (state enum) | xs, s, m, l, xl |
| **NodeStatus** | warning, error (enum) | — |
| **FileThumb** | — | sm, md |
| **PremiumBadge** | blue, indigo, gray, orange (color) | s, m, custom |
| **SegmentedControl** | 3 nested CVAs; activeState: default/accent/accentLight | regular, small, large |
| **AppIcon** | 3 nested CVAs; rounded: true/false | xs, tiny, small, medium, large, xl, xxl |
| **Badge** | Warning, Accent, Default (BadgeState enum) | s, m, l |

### 3.3 Components Wrapping @headlessui/react (9)

| Component | Headless UI Primitives |
|-----------|----------------------|
| **Dialog** | Dialog, DialogPanel, DialogTitle, Transition, TransitionChild |
| **Drawer** | Dialog, DialogBackdrop, DialogTitle |
| **Modal** | Dialog, DialogPanel, DialogTitle, Transition, TransitionChild |
| **Select** | Combobox, ComboboxButton, ComboboxInput, ComboboxOption, ComboboxOptions, Listbox, ListboxButton, ListboxOption, ListboxOptions |
| **Switch** | Switch |
| **Popover** | Popover, PopoverButton, PopoverPanel, Transition |
| **FullScreenModal** | Dialog, DialogPanel, Transition, TransitionChild |
| **ContentDialog** | Transition, TransitionChild |
| **Select (Portal)** | Uses PortalToFollowElem (@floating-ui/react) |

---

## 4. Form System

### 4.1 Input

**File**: `web/app/components/base/input/index.tsx`

```typescript
interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  size?: 'regular' | 'large'          // CVA variant
  showLeftIcon?: boolean               // Search icon
  showClearIcon?: boolean              // Clear button
  showCopyIcon?: boolean               // Copy to clipboard
  onClear?: () => void
  disabled?: boolean
  destructive?: boolean                // Error state
  wrapperClassName?: string
  unit?: string                        // Unit suffix display
}
```

Features: Leading zero removal on number inputs, integrated search/clear/copy icons.

### 4.2 Textarea

**File**: `web/app/components/base/textarea/index.tsx`

```typescript
interface TextareaProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  size?: 'small' | 'regular' | 'large'  // CVA variant
  value: string | number
  disabled?: boolean
  destructive?: boolean
}
```

### 4.3 Select (3 variants)

**File**: `web/app/components/base/select/index.tsx`

| Variant | Based On | Features |
|---------|----------|----------|
| `Select` | Headless Combobox | Searchable, filterable |
| `SimpleSelect` | Headless Listbox | Non-searchable dropdown |
| `PortalSelect` | PortalToFollowElem | Portal-based positioning |

```typescript
type Item = { value: number | string; name: string; isGroup?: boolean; disabled?: boolean; extra?: any }
```

### 4.4 Switch

**File**: `web/app/components/base/switch/index.tsx`

```typescript
interface SwitchProps {
  onChange?: (value: boolean) => void
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'l'
  defaultValue?: boolean
  disabled?: boolean
}
```

Wraps `@headlessui/react` Switch.

### 4.5 Checkbox

**File**: `web/app/components/base/checkbox/index.tsx`

```typescript
interface CheckboxProps {
  checked?: boolean
  onCheck?: (event: React.MouseEvent<HTMLDivElement>) => void
  disabled?: boolean
  indeterminate?: boolean
}
```

Custom implementation (not headless UI).

### 4.6 Radio

**File**: `web/app/components/base/radio/index.tsx`

Compound component pattern: `Radio` with `Radio.Group` attached.

### 4.7 Slider

**File**: `web/app/components/base/slider/index.tsx`

Wraps `react-slider` library:

```typescript
interface ISliderProps {
  value: number
  max?: number      // default: 100
  min?: number      // default: 0
  step?: number     // default: 1
  disabled?: boolean
  onChange: (value: number) => void
}
```

### 4.8 SegmentedControl

**File**: `web/app/components/base/segmented-control/index.tsx`

Generic component `<T extends string | number | symbol>`:

```typescript
interface SegmentedControlOption<T> {
  value: T
  text?: string
  Icon?: React.ComponentType
  count?: number
  disabled?: boolean
}
```

Uses 3 nested CVA definitions for container, item, and text wrapper.

---

## 5. Modal/Dialog System

### 5.1 Architecture

Four dialog layers, all wrapping `@headlessui/react`:

| Component | Use Case | Z-Index Behavior |
|-----------|----------|-----------------|
| **Modal** | Standard centered modal | Standard overlay |
| **Dialog** (CustomDialog) | Lightweight dialog with title/footer | Standard overlay |
| **Drawer** | Side panel | Configurable overlay (mask prop) |
| **FullScreenModal** | Full-screen takeover | Full overlay |
| **ContentDialog** | Slide-in side panel | Transition-based |
| **Confirm** | Confirmation dialog (renders in portal) | z-[100] |

### 5.2 Modal

```typescript
interface IModal {
  isShow: boolean
  onClose?: () => void
  title?: React.ReactNode
  description?: React.ReactNode
  children?: React.ReactNode
  closable?: boolean               // Show close button
  overflowVisible?: boolean
  highPriority?: boolean
  overlayOpacity?: boolean
  clickOutsideNotClose?: boolean
}
```

### 5.3 Drawer

```typescript
interface IDrawerProps {
  title?: string
  description?: string
  isOpen: boolean
  onClose: () => void
  mask?: boolean              // Show backdrop overlay
  positionCenter?: boolean
  showClose?: boolean
  clickOutsideNotOpen?: boolean
  unmount?: boolean
  noOverlay?: boolean
  footer?: React.ReactNode
}
```

### 5.4 Confirm

```typescript
interface IConfirm {
  isShow: boolean
  type?: 'info' | 'warning' | 'danger'
  title: string
  content?: React.ReactNode
  confirmText?: string | null
  onConfirm: () => void
  cancelText?: string
  onCancel: () => void
  isLoading?: boolean
  isDisabled?: boolean
  showConfirm?: boolean
  showCancel?: boolean
  maskClosable?: boolean
}
```

Keyboard support: Esc to cancel, Enter to confirm. Memoized.

### 5.5 Transition Patterns

All modals use Headless UI `Transition` with consistent patterns:

```tsx
<Transition appear show={show} as={Fragment}>
  <Dialog onClose={onClose}>
    <TransitionChild
      enter="ease-out duration-300"
      enterFrom="opacity-0"
      enterTo="opacity-100"
      leave="ease-in duration-200"
      leaveFrom="opacity-100"
      leaveTo="opacity-0"
    >
      {/* Backdrop */}
    </TransitionChild>
    <TransitionChild
      enter="ease-out duration-300"
      enterFrom="opacity-0 scale-95"
      enterTo="opacity-100 scale-100"
      leave="ease-in duration-200"
      leaveFrom="opacity-100 scale-100"
      leaveTo="opacity-0 scale-95"
    >
      {/* Panel */}
    </TransitionChild>
  </Dialog>
</Transition>
```

---

## 6. Toast/Notification System

**File**: `web/app/components/base/toast/`

### 6.1 Two APIs

**Context-based (Provider):**
```typescript
const { notify } = useToastContext()
notify({ type: 'success', message: 'Saved!' })
```

**Static/Imperative:**
```typescript
const handle = Toast.notify({ type: 'error', message: 'Failed' })
handle.clear?.() // Manual dismiss
```

### 6.2 Toast Types & Durations

| Type | Default Duration | Icon (RemixIcon) | Color Token |
|------|-----------------|-------------------|-------------|
| success | 3000ms | RiCheckboxCircleFill | `bg-toast-success-bg`, `text-text-success` |
| error | 6000ms | RiErrorWarningFill | `bg-toast-error-bg`, `text-text-destructive` |
| warning | 6000ms | RiAlertFill | `bg-toast-warning-bg`, `text-text-warning-secondary` |
| info | 3000ms | RiInformation2Fill | `bg-toast-info-bg`, `text-text-accent` |

### 6.3 Props

```typescript
interface IToastProps {
  type?: 'success' | 'error' | 'warning' | 'info'
  size?: 'md' | 'sm'
  duration?: number
  message: string
  children?: ReactNode          // Additional detail text
  onClose?: () => void
  customComponent?: ReactNode   // Inline element next to message
}
```

### 6.4 Positioning

- Fixed: top-right
- z-index: 9999
- Width: 360px

---

## 7. Loading States

### 7.1 Skeleton

**File**: `web/app/components/base/skeleton/index.tsx`

Composable primitives:

```tsx
<SkeletonContainer>          {/* flex flex-col gap-1 */}
  <SkeletonRow>              {/* flex gap-2 items-center */}
    <SkeletonRectangle />    {/* h-2 rounded-sm bg-text-quaternary opacity-20 */}
    <SkeletonPoint />        {/* "·" separator */}
  </SkeletonRow>
</SkeletonContainer>
```

Sizing via Tailwind classes on `SkeletonRectangle` (e.g., `className="h-4 w-32"`).

### 7.2 Spinner

**File**: `web/app/components/base/spinner/index.tsx`

```typescript
interface Props {
  loading?: boolean
  className?: string    // Color via text-* class
  children?: ReactNode
}
```

CSS: `border-4 border-current border-r-transparent animate-spin`. Accessible: `role="status"`, sr-only text.

### 7.3 Loading (SVG)

**File**: `web/app/components/base/loading/index.tsx`

```typescript
interface ILoadingProps {
  type?: 'area' | 'app'  // 'app' = full viewport height
}
```

Custom SVG with 4 squares + staggered opacity animation (2s cycle). `role="status"`, `aria-live="polite"`.

### 7.4 ProgressCircle

**File**: `web/app/components/base/progress-bar/progress-circle.tsx`

```typescript
interface ProgressCircleProps {
  percentage?: number              // 0-100
  size?: number                    // default: 12
  circleStrokeWidth?: number       // default: 1
  circleStrokeColor?: string
  circleFillColor?: string
  sectorFillColor?: string
}
```

SVG pie-slice rendering with arc math.

---

## 8. Icon System

### 8.1 Primary Library

**@remixicon/react** v4.7.0 — used directly throughout the codebase for UI icons.

### 8.2 Custom Icon Pipeline

**Source**: `web/app/components/base/icons/assets/` (SVG + PNG files)
**Generated**: `web/app/components/base/icons/src/` (React components + JSON)
**Script**: `web/scripts/gen-icons.mjs`

Process:
1. SVG files parsed with `@rgrove/parse-xml`
2. Converted to abstract node tree
3. Generated as React components using `IconBase.tsx`
4. Vendor icons get `currentColor` replacement for theming

### 8.3 Icon Categories

| Category | Location | Format |
|----------|----------|--------|
| UI Icons | @remixicon/react | Library import |
| Integration Logos | icons/assets/public/tracing/ | Custom SVG → React |
| LLM Provider Icons | icons/assets/public/llm/ | Custom SVG/PNG |
| Vendor Icons | icons/assets/vender/ | Custom SVG (color-replaced) |

### 8.4 IconBase Component

```typescript
interface IconBaseProps {
  data: IconData
  className?: string
  onClick?: React.MouseEventHandler<SVGSVGElement>
  style?: React.CSSProperties
  'aria-hidden'?: 'true'
}
```

---

## 9. Dark Mode

### 9.1 Implementation

| Aspect | Detail |
|--------|--------|
| **Method** | CSS custom properties with `html[data-theme]` selector |
| **Library** | `next-themes` v0.4.6 |
| **Theme values** | `light`, `dark`, `system` |
| **Hook** | `useTheme()` in `web/hooks/use-theme.ts` |
| **Token count** | 765+ CSS variables per theme |
| **Files** | `themes/light.css`, `themes/dark.css` |
| **Auto-generated** | Yes — header: "Generate by code. Don't update by hand!!!" |

### 9.2 Application

Theme variables are mapped to Tailwind utilities via `themes/tailwind-theme-var-define.ts`:

```typescript
// Example mappings
'text-primary': 'var(--color-text-primary)'
'bg-components-panel-bg': 'var(--color-components-panel-bg)'
'border-divider-regular': 'var(--color-divider-regular)'
```

Components use these semantic classes exclusively — no conditional `dark:` prefixes needed.

### 9.3 Special Handling

- Monaco editor: `monaco-sticky-fix.css` applies dark mode overrides
- VSCode CSS variable overrides for embedded editor

---

## 10. Responsive Design

### 10.1 Breakpoint Strategy

Dual system — custom tokens + standard Tailwind:

| Prefix | Width | Purpose |
|--------|-------|---------|
| `mobile:` | 100px | Base mobile |
| `tablet:` | 640px | Tablet |
| `pc:` | 769px | Desktop |
| `2k:` | 2560px | High-res |
| `sm:` | 640px | Standard Tailwind |
| `md:` | 768px | Standard Tailwind |
| `lg:` | 1024px | Standard Tailwind |
| `xl:` | 1280px | Standard Tailwind |
| `2xl:` | 1536px | Standard Tailwind |

### 10.2 Common Patterns

**Responsive grids:**
```css
grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4
```

**Conditional visibility:**
```css
hidden sm:block    /* hide on mobile */
sm:hidden          /* show only on mobile */
```

**Width adjustments:**
```css
w-fit sm:w-[248px]
sm:w-1/2
sm:min-w-[528px]
```

### 10.3 Mobile Detection

- `isMobile` state used in components
- Controls drawer mask visibility, positioning
- Feature detection in test specs (`mobile` vs `pc` viewport types)

---

## 11. Animation & Transitions

### 11.1 CSS Transitions (Primary)

Tailwind classes used consistently:

```css
transition-all duration-200 ease-in-out    /* General */
transition-colors                           /* Color changes */
transition-opacity                          /* Visibility */
transition-transform                        /* Position/scale */
```

**Known issue**: `transition-all` causes excessive animation affecting button position. Recommendation: use specific properties.

### 11.2 Headless UI Transitions

117 instances of `<Transition>` component across the codebase.

Standard patterns:
- **Modal enter**: `ease-out duration-300`, opacity 0→1, scale 95→100
- **Modal leave**: `ease-in duration-200`, opacity 1→0, scale 100→95
- **Dropdown enter**: `ease-out duration-200`, opacity + translateY
- **Sidebar**: `ease-in-out duration-300`, width/opacity

### 11.3 Custom Animations

- `animate-spin` — Tailwind built-in (loading spinners)
- `spin-slow` — Custom: `spin 2s linear infinite`
- Loading SVG — 4-path staggered opacity (0s, 0.5s, 1s, 2s delays)
- Spinner — `motion-reduce:animate-[spin_1.5s_linear_infinite]`

### 11.4 No External Animation Library

No Framer Motion, React Spring, or similar. All animation is CSS-based + Headless UI Transition.

---

## 12. Accessibility

### 12.1 ARIA Implementation

| Pattern | Usage |
|---------|-------|
| `aria-hidden="true"` | Decorative icons (11+ occurrences) |
| `aria-disabled` | Disabled interactive elements |
| `aria-label` | Modal close buttons, toggle descriptions |
| `aria-checked` | Toggle/switch states (tested) |
| `aria-live="polite"` | Loading indicators |
| `role="dialog"` | Modals, drawers |
| `role="status"` | Loading spinners, status indicators |
| `role="switch"` | Toggle controls |
| `role="button"` | Clickable non-button elements |
| `role="list"` | Markdown rendered lists |
| `role="region"` | Application sections |

### 12.2 Focus Management

- `focus-visible:outline-none` — Custom focus styles (not default ring)
- `focus-visible:bg-state-base-hover` — Visual focus indication via background
- `focus-within:border-components-input-border-active` — Container-level focus
- Focus trapped inside modals via Headless UI Dialog

### 12.3 Keyboard Navigation

21+ keyboard event handlers across the codebase:
- **Confirm dialog**: Esc to cancel, Enter to confirm
- **Form inputs**: Standard keyboard behavior
- **Menus/dropdowns**: Arrow key navigation (via Headless UI)
- **Modals**: Focus trap, Esc to close

### 12.4 Reduced Motion

```css
motion-reduce:animate-[spin_1.5s_linear_infinite]
```

Spinner component respects `prefers-reduced-motion`.

### 12.5 Screen Reader Support

- `sr-only` text for loading states ("Loading...")
- Semantic HTML5 elements throughout
- @testing-library/react tests verify aria attributes

---

## 13. Patterns & Conventions

### 13.1 CVA Pattern

```typescript
import { cva, type VariantProps } from 'class-variance-authority'

const componentVariants = cva(
  'base-classes here',
  {
    variants: {
      size: {
        small: 'px-2 py-1 text-sm',
        medium: 'px-3 py-2 text-base',
        large: 'px-4 py-3 text-lg',
      },
      variant: {
        primary: 'bg-components-button-primary-bg text-components-button-primary-text',
        secondary: 'bg-components-button-secondary-bg text-components-button-secondary-text',
      },
    },
    defaultVariants: {
      size: 'medium',
      variant: 'secondary',
    },
  }
)

type Props = HTMLAttributes & VariantProps<typeof componentVariants> & { /* custom props */ }
```

### 13.2 Semantic Token Usage

Components NEVER use raw color values. Always semantic tokens:

```tsx
// ✅ Correct
className="bg-components-panel-bg text-text-primary border-divider-regular"

// ❌ Never
className="bg-white text-gray-900 border-gray-200"
```

### 13.3 cn() Utility

All conditional class merging uses `cn()` (likely `clsx` + `tailwind-merge`):

```tsx
className={cn('base-classes', variant === 'primary' && 'primary-classes', className)}
```

### 13.4 Component File Structure

```
component-name/
├── index.tsx          # Main component + exports
├── index.css          # Optional custom CSS/animations
├── style.css          # Alternative CSS file name
└── types.ts           # Optional type definitions
```

### 13.5 Memoization

Performance-critical components use `React.memo`:
- Avatar, Tooltip, AppIcon, Confirm, Switch

### 13.6 Portal Pattern

Floating elements use custom `PortalToFollowElem` (wraps @floating-ui/react) for proper stacking context management.

### 13.7 Compound Components

Radio uses compound pattern: `Radio.Group` attached to `Radio`.

### 13.8 Generic Components

`SegmentedControl<T>` and `Select` use TypeScript generics for type-safe value handling.

---

## Appendix: Key File References

| File | Purpose |
|------|---------|
| `web/tailwind-common-config.ts` | Colors, shadows, screens, fonts, animations |
| `web/themes/tailwind-theme-var-define.ts` | 765+ CSS var → Tailwind utility mappings |
| `web/themes/light.css` | Light theme token values |
| `web/themes/dark.css` | Dark theme token values |
| `web/app/styles/globals.css` | Border radius scale, typography utilities |
| `web/app/styles/preflight.css` | Custom CSS reset |
| `web/typography.js` | Prose/markdown typography config |
| `web/hooks/use-theme.ts` | Theme switching hook |
| `web/scripts/gen-icons.mjs` | Icon generation pipeline |
| `web/app/components/base/` | 101 base component directories |
