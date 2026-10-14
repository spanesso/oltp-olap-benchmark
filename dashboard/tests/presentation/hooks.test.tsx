import { describe, it, expect, vi, beforeEach } from "vitest";
import { act, renderHook, waitFor } from "@testing-library/react";
import { useBenchmarkData } from "../../src/presentation/hooks/useBenchmarkData";
import { useBoroughStats } from "../../src/presentation/hooks/useBoroughStats";
import { useExperiments } from "../../src/presentation/hooks/useExperiments";
import { FALLBACK_BOROUGH_STATS } from "../../src/domain/entities/BoroughStat";
import * as repository from "../../src/infrastructure/repositories/BenchmarkRepository";

vi.mock("../../src/infrastructure/repositories/BenchmarkRepository");

const mocked = vi.mocked(repository);
const results = { profile: "full" } as never;

beforeEach(() => {
  vi.resetAllMocks();
});

describe("useBenchmarkData", () => {
  it("starts loading and exposes the data once fetched", async () => {
    mocked.fetchBenchmarkResults.mockResolvedValue(results);
    const { result } = renderHook(() => useBenchmarkData());
    expect(result.current.loading).toBe(true);
    await waitFor(() => expect(result.current.loading).toBe(false));
    expect(result.current.data).toBe(results);
    expect(result.current.error).toBeNull();
  });

  it("exposes the error message when the load fails", async () => {
    mocked.fetchBenchmarkResults.mockRejectedValue(new Error("boom"));
    const { result } = renderHook(() => useBenchmarkData());
    await waitFor(() => expect(result.current.loading).toBe(false));
    expect(result.current.error).toBe("boom");
    expect(result.current.data).toBeNull();
  });

  it("replaces the data after a live run and clears running", async () => {
    const fresh = { profile: "fresh" } as never;
    mocked.fetchBenchmarkResults.mockResolvedValue(results);
    mocked.runLiveBenchmark.mockResolvedValue(fresh);
    const { result } = renderHook(() => useBenchmarkData());
    await waitFor(() => expect(result.current.loading).toBe(false));
    act(() => result.current.triggerLiveRun());
    await waitFor(() => expect(result.current.data).toBe(fresh));
    expect(result.current.running).toBe(false);
  });

  it("keeps the existing data when a live run fails", async () => {
    mocked.fetchBenchmarkResults.mockResolvedValue(results);
    mocked.runLiveBenchmark.mockRejectedValue(new Error("server down"));
    const { result } = renderHook(() => useBenchmarkData());
    await waitFor(() => expect(result.current.loading).toBe(false));
    act(() => result.current.triggerLiveRun());
    await waitFor(() => expect(result.current.runError).toBe("server down"));
    expect(result.current.data).toBe(results);
    expect(result.current.error).toBeNull();
  });
});

describe("useBoroughStats", () => {
  it("returns live stats when the API server answers", async () => {
    const live = [{ borough: "BRONX", count: 5 }];
    mocked.fetchBoroughStats.mockResolvedValue(live);
    const { result } = renderHook(() => useBoroughStats());
    await waitFor(() => expect(result.current.stats).toEqual(live));
    expect(result.current.usingFallback).toBe(false);
  });

  it("falls back to approximate stats when the server is unreachable", async () => {
    mocked.fetchBoroughStats.mockRejectedValue(new Error("offline"));
    const { result } = renderHook(() => useBoroughStats());
    await waitFor(() => expect(result.current.stats).toEqual(FALLBACK_BOROUGH_STATS));
    expect(result.current.usingFallback).toBe(true);
  });
});

describe("useExperiments", () => {
  it("returns the report when it exists", async () => {
    const report = { queries: [] } as never;
    mocked.fetchExperiments.mockResolvedValue(report);
    const { result } = renderHook(() => useExperiments());
    await waitFor(() => expect(result.current).toBe(report));
  });

  it("stays null when there is no report or loading fails", async () => {
    mocked.fetchExperiments.mockRejectedValue(new Error("offline"));
    const { result } = renderHook(() => useExperiments());
    await waitFor(() => expect(mocked.fetchExperiments).toHaveBeenCalled());
    expect(result.current).toBeNull();
  });
});
