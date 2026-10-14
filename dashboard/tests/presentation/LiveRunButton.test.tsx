import { describe, it, expect, vi, afterEach } from "vitest";
import { act, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { LiveRunButton } from "../../src/presentation/components/LiveRunButton";
import { renderWithI18n } from "../utils";

afterEach(() => {
  vi.useRealTimers();
});

describe("LiveRunButton", () => {
  it("shows the button when idle and calls onRun when clicked", async () => {
    const onRun = vi.fn();
    renderWithI18n(<LiveRunButton running={false} onRun={onRun} runError={null} />);
    await userEvent.click(screen.getByRole("button", { name: /Refresh live measurement/ }));
    expect(onRun).toHaveBeenCalledTimes(1);
  });

  it("replaces the button with a status line while running", () => {
    renderWithI18n(<LiveRunButton running onRun={() => {}} runError={null} />);
    expect(screen.queryByRole("button")).not.toBeInTheDocument();
    expect(screen.getByText(/Measuring 6 queries/)).toBeInTheDocument();
  });

  it("counts elapsed seconds while running", () => {
    vi.useFakeTimers();
    renderWithI18n(<LiveRunButton running onRun={() => {}} runError={null} />);
    expect(screen.getByText("0:00")).toBeInTheDocument();
    act(() => {
      vi.advanceTimersByTime(65_000);
    });
    expect(screen.getByText("1:05")).toBeInTheDocument();
  });

  it("translates a connection failure into an actionable message", () => {
    renderWithI18n(
      <LiveRunButton running={false} onRun={() => {}} runError="Failed to fetch" />,
    );
    expect(screen.getByText(/Could not reach the server/)).toBeInTheDocument();
  });

  it("shows any other error as received", () => {
    renderWithI18n(
      <LiveRunButton running={false} onRun={() => {}} runError="benchmark.py exited 4" />,
    );
    expect(screen.getByText("benchmark.py exited 4")).toBeInTheDocument();
  });

  it("hides the error while a new run is in progress", () => {
    renderWithI18n(<LiveRunButton running onRun={() => {}} runError="old error" />);
    expect(screen.queryByText("old error")).not.toBeInTheDocument();
  });
});
