export interface BoroughStat {
  borough: string;
  count: number;
}

// Approximate distribution of the 5M-row full profile. Shown when the API
// server is not running, so the map still renders (and is labelled as approximate).
export const FALLBACK_BOROUGH_STATS: BoroughStat[] = [
  { borough: "BROOKLYN", count: 1_280_000 },
  { borough: "QUEENS", count: 1_140_000 },
  { borough: "MANHATTAN", count: 850_000 },
  { borough: "BRONX", count: 670_000 },
  { borough: "STATEN ISLAND", count: 210_000 },
];
