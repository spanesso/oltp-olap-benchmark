import { describe, it, expect } from "vitest";
import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { SchemaViewer } from "../../src/presentation/components/SchemaViewer";
import { renderWithI18n } from "../utils";

describe("SchemaViewer", () => {
  it("shows the normalized OLTP tables by default", () => {
    renderWithI18n(<SchemaViewer />);
    expect(screen.getByText("service_request")).toBeInTheDocument();
    expect(screen.getByText("complaint_descriptor")).toBeInTheDocument();
    expect(screen.queryByText("fact_service_request")).not.toBeInTheDocument();
  });

  it("switches to the star schema on the OLAP tab", async () => {
    renderWithI18n(<SchemaViewer />);
    await userEvent.click(screen.getByRole("button", { name: /OLAP/ }));
    expect(screen.getByText("fact_service_request")).toBeInTheDocument();
    for (const dimension of [
      "dim_date",
      "dim_agency",
      "dim_complaint",
      "dim_location",
      "dim_channel",
      "dim_status",
    ]) {
      expect(screen.getByText(dimension)).toBeInTheDocument();
    }
  });

  it("switches to the raw staging table on the Staging tab", async () => {
    renderWithI18n(<SchemaViewer />);
    await userEvent.click(screen.getByRole("button", { name: /Staging/ }));
    expect(screen.getByText("service_request_raw")).toBeInTheDocument();
  });
});
