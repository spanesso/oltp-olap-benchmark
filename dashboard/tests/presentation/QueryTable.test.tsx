import { describe, it, expect } from "vitest";
import { screen } from "@testing-library/react";
import { renderWithI18n } from "../utils";
import { QueryTable } from "../../src/presentation/components/QueryTable";

const data = [
  { label: "q1", question: "How many?", oltp: 2400, olap: 30, speedup: 80 },
  { label: "q2", question: "Top types?", oltp: 1200, olap: 20, speedup: 60 },
];

describe("QueryTable", () => {
  it("renders all rows", () => {
    renderWithI18n(<QueryTable data={data} />);
    expect(screen.getByText("q1")).toBeInTheDocument();
    expect(screen.getByText("q2")).toBeInTheDocument();
  });

  it("shows speedup badges", () => {
    renderWithI18n(<QueryTable data={data} />);
    expect(screen.getByText("80.0x")).toBeInTheDocument();
    expect(screen.getByText("60.0x")).toBeInTheDocument();
  });

  it("renders table headers", () => {
    renderWithI18n(<QueryTable data={data} />);
    expect(screen.getByText("Query")).toBeInTheDocument();
    expect(screen.getByText("OLTP (ms)")).toBeInTheDocument();
    expect(screen.getByText("OLAP (ms)")).toBeInTheDocument();
    expect(screen.getByText("Speedup")).toBeInTheDocument();
  });

  it("translates the headers when the language is Spanish", () => {
    renderWithI18n(<QueryTable data={data} />, "es");
    expect(screen.getByText("Pregunta")).toBeInTheDocument();
    expect(screen.queryByText("Question")).not.toBeInTheDocument();
  });

  it("renders empty for no data", () => {
    renderWithI18n(<QueryTable data={[]} />);
    const rows = screen.queryAllByRole("row");
    expect(rows).toHaveLength(1); // header only
  });
});
