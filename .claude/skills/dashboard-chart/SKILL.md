# Skill: Dashboard Chart

Create a data visualization component for a React + TypeScript dashboard. Extends
`/dashboard-module` with charting-specific guidance: chart type selection, Recharts
integration, color palettes, responsive sizing, accessibility, and dark mode.

## When to use

Invoke with `/dashboard-chart <chart-name>` when the module being built is a chart, graph,
or data visualization. It follows the same Clean Architecture steps as `/dashboard-module`
but adds chart-specific patterns.

## Chart type selection

Pick the chart type based on the data relationship:

| Relationship | Chart type | Recharts component |
|---|---|---|
| Compare values across categories | Horizontal bar | `<BarChart layout="vertical">` |
| Compare two series side by side | Grouped bar | `<BarChart>` with two `<Bar>` |
| Show change over time | Line | `<LineChart>` |
| Show proportions of a whole | Stacked bar or pie | `<BarChart>` or `<PieChart>` |
| Show distribution | Box plot or histogram | Custom with `<BarChart>` |
| Single KPI value | Stat tile | Custom `<div>` with large number |

For the benchmark dashboard: use **grouped bar charts** to compare OLTP vs OLAP times
(two bars per query, log scale for the time axis since the difference is 50-180x).

## Color system

Define colors as CSS custom properties on `:root` for theme support:

```css
:root {
  --color-oltp: #6366f1;         /* indigo — the slower model */
  --color-olap: #10b981;         /* emerald — the faster model */
  --color-speedup: #f59e0b;      /* amber — the multiplier */
  --color-surface: #ffffff;
  --color-text: #1f2937;
  --color-text-secondary: #6b7280;
  --color-border: #e5e7eb;
}

@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --color-surface: #111827;
    --color-text: #f9fafb;
    --color-text-secondary: #9ca3af;
    --color-border: #374151;
  }
}
```

Use `var(--color-oltp)` and `var(--color-olap)` consistently across all charts so the
viewer learns the association once.

## Recharts component pattern

```tsx
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer
} from 'recharts';

interface Props {
  data: ChartData[];
}

export function ComparisonChart({ data }: Props) {
  return (
    <ResponsiveContainer width="100%" height={400}>
      <BarChart data={data} layout="vertical" margin={{ left: 120 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
        <XAxis
          type="number"
          scale="log"
          domain={['auto', 'auto']}
          tickFormatter={(v) => `${v.toLocaleString()} ms`}
        />
        <YAxis type="category" dataKey="label" width={110} />
        <Tooltip
          formatter={(value: number) => `${value.toLocaleString()} ms`}
          contentStyle={{ background: 'var(--color-surface)' }}
        />
        <Legend />
        <Bar dataKey="oltp" name="OLTP (PostgreSQL)" fill="var(--color-oltp)" />
        <Bar dataKey="olap" name="OLAP (DuckDB)" fill="var(--color-olap)" />
      </BarChart>
    </ResponsiveContainer>
  );
}
```

## Responsive design

- Always wrap charts in `<ResponsiveContainer width="100%" height={N}>`
- On mobile (< 640px): stack charts vertically, reduce height to 250px
- On desktop: charts can sit side by side in a grid
- Use CSS grid or flexbox, not fixed widths
- Minimum touch target: 44x44px for interactive elements

## Accessibility

- Every chart must have an `aria-label` describing what it shows
- Include a visually-hidden `<table>` with the same data for screen readers
- Use sufficient color contrast (4.5:1 minimum for text on background)
- Tooltips should be keyboard-navigable

## Stat tiles (KPI cards)

For single-number highlights (total speedup, number of queries, data volume):

```tsx
interface StatProps {
  label: string;
  value: string | number;
  unit?: string;
  accent?: string;
}

export function StatTile({ label, value, unit, accent }: StatProps) {
  return (
    <div className="stat-tile">
      <span className="stat-label">{label}</span>
      <span className="stat-value" style={{ color: accent }}>
        {typeof value === 'number' ? value.toLocaleString() : value}
      </span>
      {unit && <span className="stat-unit">{unit}</span>}
    </div>
  );
}
```

## Testing charts

- **Snapshot test**: render with fixed data, verify no regression
- **Data mapping test**: verify the chart receives the correct transformed data
- **Accessibility test**: check for `aria-label` and the hidden data table
- Don't test Recharts internals (SVG paths, etc.) — trust the library

## Checklist (verify before marking done)

- [ ] Chart type matches the data relationship (see table above)
- [ ] Colors use CSS custom properties, not hardcoded values
- [ ] Dark mode works via `prefers-color-scheme` media query
- [ ] Chart is wrapped in `<ResponsiveContainer>`
- [ ] Chart has an `aria-label` and a hidden data table
- [ ] Tooltip shows formatted values with units
- [ ] Component receives data via props (Clean Architecture)
- [ ] Domain use case transforms raw data into chart-ready format
- [ ] Tests cover rendering and accessibility
- [ ] Mobile layout works at 320px width
