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
