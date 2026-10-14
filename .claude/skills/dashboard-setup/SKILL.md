# Skill: Dashboard Setup

Initialize a React + TypeScript + Vite project with Clean Architecture structure, testing
infrastructure, and professional tooling.

## When to use

Invoke with `/dashboard-setup` when starting a new dashboard or front-end sub-project
inside an existing repository. The skill creates the directory structure, installs
dependencies, and configures build and test tooling.

## Input

- `PROJECT_DIR`: path where the dashboard will live (e.g. `dashboard/`)
- `DATA_SOURCE`: description of what the dashboard visualizes (e.g. "benchmark results JSON")

## Execution Steps

### 1. Create the directory structure (Clean Architecture)

```
{PROJECT_DIR}/
  src/
    domain/
      entities/          # Pure TypeScript interfaces and types. No framework imports.
      usecases/          # Pure functions: business logic. No React, no I/O.
    infrastructure/
      repositories/      # Data access: fetch JSON, call APIs, read files.
    presentation/
      components/        # React components. Each in its own directory:
                         #   ComponentName/
                         #     ComponentName.tsx
                         #     ComponentName.test.tsx
                         #     index.ts          (re-export)
      hooks/             # Custom React hooks.
      pages/             # Page-level components that compose smaller ones.
    App.tsx              # Root component with routing (if needed).
    main.tsx             # Entry point: ReactDOM.createRoot.
  tests/
    domain/              # Unit tests for entities and use cases.
    presentation/        # Component tests (React Testing Library).
    setup.ts             # Test setup: jsdom, cleanup.
  public/                # Static assets.
  index.html             # Vite entry HTML.
  package.json
  tsconfig.json
  tsconfig.node.json
  vite.config.ts
  vitest.config.ts
```

### 2. Dependencies

**Runtime:**
- `react` and `react-dom` (18.x)
- `recharts` (charting library — lightweight, React-native, typed)

**Dev:**
- `typescript` (5.x)
- `vite` and `@vitejs/plugin-react`
- `vitest`, `@testing-library/react`, `@testing-library/jest-dom`, `jsdom`
- `eslint`, `@typescript-eslint/eslint-plugin`, `@typescript-eslint/parser`

Install with: `npm create vite@latest {PROJECT_DIR} -- --template react-ts`, then add
the testing and charting deps.

### 3. Configuration files

**tsconfig.json**: strict mode, path aliases (`@domain/*`, `@infra/*`, `@presentation/*`).

**vite.config.ts**: resolve aliases matching tsconfig paths.

**vitest.config.ts**: jsdom environment, setup file, coverage thresholds.

### 4. Clean Architecture rules (enforce in code review)

| Layer | May import from | Must NOT import from |
|-------|----------------|---------------------|
| `domain/entities` | Nothing (pure types) | infrastructure, presentation |
| `domain/usecases` | `domain/entities` | infrastructure, presentation, React |
| `infrastructure` | `domain/entities` | presentation, React |
| `presentation` | All layers | — |

The dependency arrow always points inward: **presentation → infrastructure → domain**.

### 5. Smoke test

After setup, verify:
- `npm run dev` serves the app on localhost
- `npm run build` produces a production bundle
- `npm run test` finds and runs at least one test
- `npm run lint` passes

## Output

The skill creates the project directory, installs dependencies, and prints the localhost URL.
The project is ready for modules to be added with `/dashboard-module`.
