import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { PipelineDiagram } from "../../src/presentation/components/PipelineDiagram";

describe("PipelineDiagram", () => {
  it("renders all pipeline steps", () => {
    render(<PipelineDiagram />);
    expect(screen.getByText("NYC 311 API")).toBeInTheDocument();
    expect(screen.getByText("Staging")).toBeInTheDocument();
    expect(screen.getByText("OLTP Model")).toBeInTheDocument();
    expect(screen.getByText("OLAP Model")).toBeInTheDocument();
    expect(screen.getByText("Benchmark")).toBeInTheDocument();
    expect(screen.getByText("Results")).toBeInTheDocument();
  });

  it("has an accessible role and label", () => {
    render(<PipelineDiagram />);
    const diagram = screen.getByRole("img");
    expect(diagram).toHaveAttribute(
      "aria-label",
      "Data pipeline from API to results",
    );
  });
});
