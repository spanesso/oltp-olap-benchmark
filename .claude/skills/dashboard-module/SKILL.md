# Skill: Dashboard Module

Create a feature module for a React + TypeScript dashboard following Clean Architecture.
Each module touches all three layers (domain, infrastructure, presentation) and ships with
its own tests.

## When to use

Invoke with `/dashboard-module <feature-name>` after the project has been set up with
`/dashboard-setup`. Use it for each new feature: a chart, a table, a card, a panel, etc.

## Input

- `FEATURE_NAME`: kebab-case name (e.g. `speedup-chart`, `query-table`)
- `DESCRIPTION`: what the module shows or does
- `DATA_SHAPE`: the TypeScript interface for the data it consumes

## Execution Steps — follow this order exactly

### Step 1: Define the entity (domain layer)

Create `src/domain/entities/{FeatureName}.ts`:

```typescript
// Pure TypeScript interface. No framework imports.
export interface FeatureName {
  // fields matching the data shape
}
```

**Rules:**
- Only types, interfaces, and constants
- Zero imports from outside `domain/`
- Export everything — other layers depend on these types

### Step 2: Write the use case (domain layer)

Create `src/domain/usecases/{featureAction}.ts`:

```typescript
import type { Entity } from '../entities/Entity';

// Pure function. No side effects, no React, no I/O.
export function transformData(raw: RawData): Entity[] {
  // business logic here
}
```

**Rules:**
- Pure functions only (input → output, no mutation)
- May import from `domain/entities/`
- Must NOT import React, fetch, or any framework
- Should be independently testable

### Step 3: Write the repository (infrastructure layer)

Create `src/infrastructure/repositories/{Feature}Repository.ts`:

```typescript
import type { Entity } from '../../domain/entities/Entity';

export async function fetchData(): Promise<Entity[]> {
  // I/O lives here: fetch JSON, read file, call API
}
```

**Rules:**
- May import from `domain/entities/`
- Must NOT import React
- Handles all I/O: fetch, localStorage, file reads

### Step 4: Create the React component (presentation layer)

Create `src/presentation/components/{FeatureName}/{FeatureName}.tsx`:

```typescript
import type { Entity } from '../../../domain/entities/Entity';

interface Props {
  data: Entity[];       // the component receives data, never fetches it
  // other presentation-only props
}

export function FeatureName({ data }: Props) {
  // React component
}
```

**Rules:**
- Receives data via props — never calls repositories directly
- May call use cases for transformations
- Each component in its own directory with an `index.ts` re-export
- Responsive: works at phone width (min 320px) and desktop

### Step 5: Create the custom hook (presentation layer, optional)

Create `src/presentation/hooks/use{Feature}.ts` if the component needs state management
or data loading:

```typescript
import { useState, useEffect } from 'react';
import { fetchData } from '../../infrastructure/repositories/FeatureRepository';
import { transformData } from '../../domain/usecases/featureAction';

export function useFeature() {
  const [data, setData] = useState<Entity[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchData()
      .then(transformData)
      .then(setData)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  return { data, loading, error };
}
```

The hook is the bridge between infrastructure and presentation.

### Step 6: Write tests

**Domain tests** (`tests/domain/test-{feature}.test.ts`):
- Test use case pure functions with known inputs and expected outputs
- Test edge cases: empty arrays, null values, extreme numbers
- No mocking needed — these are pure functions

**Component tests** (`src/presentation/components/{FeatureName}/{FeatureName}.test.tsx`):
- Use React Testing Library
- Test that the component renders data correctly
- Test loading and error states if applicable
- Test user interactions (click, hover) if applicable
- Prefer `getByRole` and `getByText` over `getByTestId`

```typescript
import { render, screen } from '@testing-library/react';
import { FeatureName } from './FeatureName';

describe('FeatureName', () => {
  it('renders the data', () => {
    render(<FeatureName data={mockData} />);
    expect(screen.getByText('expected text')).toBeInTheDocument();
  });
});
```

### Step 7: Export and integrate

- Add `index.ts` in the component directory re-exporting the component
- Import the component in the page that uses it
- Verify with `npm run test` and `npm run lint`

## Checklist (verify before marking done)

- [ ] Entity is a pure interface in `domain/entities/`
- [ ] Use case is a pure function in `domain/usecases/`
- [ ] Repository handles I/O in `infrastructure/repositories/`
- [ ] Component receives data via props, not direct I/O
- [ ] Component directory has: `Component.tsx`, `Component.test.tsx`, `index.ts`
- [ ] Domain tests cover the use case with edge cases
- [ ] Component tests verify rendering with React Testing Library
- [ ] No layer imports from a layer it should not (see dependency table in `/dashboard-setup`)
- [ ] `npm run test` passes
- [ ] `npm run lint` passes
