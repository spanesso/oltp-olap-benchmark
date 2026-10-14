import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { StatTile } from "../../src/presentation/components/StatTile";

describe("StatTile", () => {
  it("renders label and string value", () => {
    render(<StatTile label="Status" value="Reached" />);
    expect(screen.getByText("Status")).toBeInTheDocument();
    expect(screen.getByText("Reached")).toBeInTheDocument();
  });

  it("formats numeric value with locale separators", () => {
    render(<StatTile label="Volume" value={5000000} />);
    expect(screen.getByText(/5.*000.*000/)).toBeInTheDocument();
  });

  it("renders unit when provided", () => {
    render(<StatTile label="Volume" value={5000} unit="rows" />);
    expect(screen.getByText("rows")).toBeInTheDocument();
  });

  it("applies accent color to value", () => {
    render(<StatTile label="Speed" value="55x" accent="red" />);
    const value = screen.getByText("55x");
    expect(value).toHaveStyle({ color: "rgb(255, 0, 0)" });
  });

  it("does not set color when no accent", () => {
    render(<StatTile label="Speed" value="55x" />);
    const value = screen.getByText("55x");
    expect(value.style.color).toBe("");
  });
});
