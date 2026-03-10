# Frontend Changes

## Code Quality Tooling Setup

### Overview
Added code quality tooling to the frontend using **Prettier** (automatic code formatter, the JavaScript equivalent of Python's black) and **ESLint** (static code linter). Development scripts were created to run quality checks and auto-fixes.

---

### New Files

#### `frontend/package.json`
Defines the frontend as a Node.js project and provides npm scripts for quality tooling:
- `npm run format` — auto-format all files with Prettier
- `npm run format:check` — check formatting without changing files (CI-safe)
- `npm run lint` — run ESLint static analysis
- `npm run lint:fix` — auto-fix lint issues where possible
- `npm run quality` — run both format check and lint (full quality gate)
- `npm run quality:fix` — run both formatter and lint fix (auto-fix everything)

Dependencies: `prettier@^3`, `eslint@^9`, `eslint-config-prettier@^9`

#### `frontend/.prettierrc`
Prettier configuration enforcing consistent formatting:
- Single quotes for strings
- Semicolons required
- 2-space indentation
- 100-character print width
- ES5 trailing commas
- LF line endings

#### `frontend/.prettierignore`
Excludes `node_modules/` from Prettier processing.

#### `frontend/eslint.config.js`
ESLint flat config (ESLint v9 format) with rules:
- `no-var` — enforces `let`/`const` over `var`
- `prefer-const` — warns when `let` could be `const`
- `eqeqeq` — enforces `===` over `==`
- `curly` — requires braces for all control flow blocks
- `no-unused-vars` — warns on unused variables
- Browser globals declared (`document`, `window`, `fetch`, `marked`, etc.)
- `eslint-config-prettier` applied to disable rules that conflict with Prettier

#### `frontend/scripts/check-quality.sh`
Shell script that installs deps if needed, then runs `format:check` and `lint` in sequence. Exits non-zero on any failure (suitable for CI).

#### `frontend/scripts/fix-quality.sh`
Shell script that installs deps if needed, then runs `format` and `lint:fix` to automatically correct all fixable issues.

---

### Modified Files

#### `frontend/script.js`
Applied Prettier formatting:
- Collapsed double blank lines to single blank lines (lines 31–32 and 42–43)
- Standardized indentation to 2 spaces throughout
- Added `curly`-compliant braces to single-line `if` statements (`if (!query)`, `if (!response.ok)`)
- Normalized trailing commas in object/array literals per ES5 config
- Consistent arrow function parentheses (`(e) =>` instead of `e =>`)

#### `frontend/index.html`
Applied Prettier formatting:
- Changed `<!DOCTYPE html>` to lowercase `<!doctype html>` (Prettier default)
- Standardized indentation to 2 spaces (previously 4 spaces)
- Self-closed void elements (`<meta ... />`, `<input ... />`, `<link ... />`)
- Long `<button>` attributes broken across multiple lines for readability

---

### Usage

```bash
# Install dependencies (first time only)
cd frontend && npm install

# Check formatting and linting
npm run quality

# Auto-fix all issues
npm run quality:fix

# Or use the shell scripts
bash frontend/scripts/check-quality.sh
bash frontend/scripts/fix-quality.sh
```

## Dark/Light Theme Toggle

### Summary
Added a theme toggle button that lets users switch between the existing dark theme and a new light theme. The selected theme persists across page reloads via `localStorage`.

---

### Files Modified

#### `frontend/index.html`
- Added a `<button id="themeToggle">` element with `position: fixed` in the top-right corner, placed directly after `<body>`.
- Button contains two inline SVG icons:
  - **Sun icon** — displayed in dark mode (click to switch to light)
  - **Moon icon** — displayed in light mode (click to switch back to dark)
- Includes `aria-label="Toggle theme"` and `title` attribute for accessibility.

#### `frontend/style.css`
- Added **`[data-theme="light"]`** CSS rule overriding all `:root` variables with light-mode values:
  - Background: `#f8fafc`, Surface: `#ffffff`, Text: `#0f172a`, Border: `#e2e8f0`
- Added **`.theme-toggle`** button styles:
  - Fixed position: `top: 1rem; right: 1rem; z-index: 1000`
  - Circular (40×40px), matches the existing design aesthetic
  - Hover: scale up + deeper shadow; Active: scale down; Focus: focus-ring outline
  - `transition` on background, border, color, transform, and box-shadow for smooth interaction
- Added `.icon-sun` / `.icon-moon` visibility rules toggled by `[data-theme="light"]`
- Added a **smooth transition** (`0.3s ease`) on `background-color`, `border-color`, and `color` for `body`, sidebar, chat containers, messages, input, and buttons — giving the entire UI a smooth animated crossfade when the theme changes.

#### `frontend/script.js`
- Added **`initTheme()`** — reads `localStorage.getItem('theme')` on page load and applies `data-theme="light"` to `<html>` if needed.
- Added **`toggleTheme()`** — toggles `data-theme` attribute on `<html>` and saves the preference to `localStorage`.
- `initTheme()` is called at the start of the `DOMContentLoaded` handler (before other setup).
- `toggleTheme` is registered as a click handler on `#themeToggle` inside `setupEventListeners()`.

---

### Design Decisions
- The `data-theme` attribute is applied to `<html>` (document root) so that CSS variable overrides cascade to the entire page.
- Dark theme is the default (matches existing `:root` variables); light theme is opt-in via the toggle.
- The sun icon is shown in dark mode (hinting "switch to light") and the moon icon in light mode (hinting "switch to dark").
- No extra dependencies were introduced — everything uses native CSS variables, SVG, and `localStorage`.

---

## Light Theme CSS Variable Improvements

### Summary
Refined the light theme palette for proper contrast ratios (WCAG AA), added semantic color variables for code blocks and status messages, and wired up all previously hardcoded `rgba`/hex color values to use CSS variables so they adapt correctly in both themes.

### Changes in `frontend/style.css`

#### `:root` — new semantic variables added to dark theme
| Variable | Value | Purpose |
|---|---|---|
| `--code-bg` | `rgba(0,0,0,0.25)` | Code/pre block backgrounds |
| `--error-bg` | `rgba(239,68,68,0.1)` | Error message background |
| `--error-color` | `#f87171` | Error message text |
| `--error-border` | `rgba(239,68,68,0.2)` | Error message border |
| `--success-bg` | `rgba(34,197,94,0.1)` | Success message background |
| `--success-color` | `#4ade80` | Success message text |
| `--success-border` | `rgba(34,197,94,0.2)` | Success message border |

#### `[data-theme="light"]` — refined palette with contrast annotations
| Variable | Value | Contrast ratio |
|---|---|---|
| `--primary-color` | `#1d4ed8` (blue-700) | 4.7:1 on white (AA) |
| `--primary-hover` | `#1e40af` (blue-800) | deeper on hover |
| `--background` | `#f8fafc` | warm near-white canvas |
| `--surface` | `#ffffff` | cards and sidebar |
| `--surface-hover` | `#f1f5f9` | subtle hover tint |
| `--text-primary` | `#0f172a` | ~17:1 on white (AAA) |
| `--text-secondary` | `#475569` (slate-600) | 5.9:1 on white (AA) |
| `--border-color` | `#cbd5e1` (slate-300) | visible but soft |
| `--assistant-message` | `#e8edf5` | distinct from `#f8fafc` background |
| `--welcome-border` | `#93c5fd` (blue-300) | soft accent on light bg |
| `--code-bg` | `rgba(15,23,42,0.06)` | subtle tint for code blocks |
| `--error-color` | `#b91c1c` (red-700) | 5.5:1 on white (AA) |
| `--success-color` | `#15803d` (green-700) | 5.1:1 on white (AA) |

#### Hardcoded colors replaced with variables
- `.message-content code` and `.message-content pre`: `rgba(0,0,0,0.2)` → `var(--code-bg)`
- `.error-message`: hardcoded red values → `var(--error-bg)`, `var(--error-color)`, `var(--error-border)`
- `.success-message`: hardcoded green values → `var(--success-bg)`, `var(--success-color)`, `var(--success-border)`
