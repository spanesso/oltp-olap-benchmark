import { describe, it, expect, vi, afterEach } from "vitest";
import {
  fetchBenchmarkResults,
  fetchBoroughStats,
  runLiveBenchmark,
} from "../../src/infrastructure/repositories/BenchmarkRepository";

function mockFetch(response: Partial<Response> & { json: () => Promise<unknown> }) {
  const fn = vi.fn().mockResolvedValue({ ok: true, status: 200, ...response });
  vi.stubGlobal("fetch", fn);
  return fn;
}

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("fetchBenchmarkResults", () => {
  it("reads the static JSON served by Vite", async () => {
    const fn = mockFetch({ json: async () => ({ profile: "full" }) });
    const result = await fetchBenchmarkResults();
    expect(fn).toHaveBeenCalledWith("/benchmark_full.json");
    expect(result).toEqual({ profile: "full" });
  });

  it("throws with the status code when the file cannot be loaded", async () => {
    mockFetch({ ok: false, status: 404, json: async () => ({}) });
    await expect(fetchBenchmarkResults()).rejects.toThrow("404");
  });
});

describe("runLiveBenchmark", () => {
  it("posts the profile to the API server and returns the new results", async () => {
    const fn = mockFetch({ json: async () => ({ profile: "quick" }) });
    const result = await runLiveBenchmark("quick");
    const [url, init] = fn.mock.calls[0];
    expect(url).toBe("http://localhost:8788/api/benchmark/run");
    expect(init.method).toBe("POST");
    expect(JSON.parse(init.body)).toEqual({ profile: "quick" });
    expect(result).toEqual({ profile: "quick" });
  });

  it("defaults to the full profile", async () => {
    const fn = mockFetch({ json: async () => ({}) });
    await runLiveBenchmark();
    expect(JSON.parse(fn.mock.calls[0][1].body)).toEqual({ profile: "full" });
  });

  it("surfaces the error message sent by the server", async () => {
    mockFetch({ ok: false, status: 500, json: async () => ({ error: "benchmark.py exited 4" }) });
    await expect(runLiveBenchmark()).rejects.toThrow("benchmark.py exited 4");
  });

  it("falls back to the status code when the error body is not JSON", async () => {
    mockFetch({
      ok: false,
      status: 502,
      json: async () => {
        throw new Error("not json");
      },
    });
    await expect(runLiveBenchmark()).rejects.toThrow("Server error 502");
  });
});

describe("fetchBoroughStats", () => {
  it("returns the borough list from the API server", async () => {
    const fn = mockFetch({
      json: async () => ({ boroughs: [{ borough: "BROOKLYN", count: 10 }] }),
    });
    const stats = await fetchBoroughStats();
    expect(fn).toHaveBeenCalledWith("http://localhost:8788/api/borough-stats");
    expect(stats).toEqual([{ borough: "BROOKLYN", count: 10 }]);
  });

  it("throws when the server is not ready", async () => {
    mockFetch({ ok: false, status: 503, json: async () => ({}) });
    await expect(fetchBoroughStats()).rejects.toThrow("503");
  });
});
