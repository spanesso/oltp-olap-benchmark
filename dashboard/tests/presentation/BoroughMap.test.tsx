import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { BoroughMap } from "../../src/presentation/components/BoroughMap";
import { renderWithI18n } from "../utils";

beforeEach(() => {
  localStorage.removeItem("gmaps_api_key");
  vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("offline")));
});

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("BoroughMap", () => {
  it("asks for a Google Maps key when none is stored", () => {
    renderWithI18n(<BoroughMap />);
    expect(screen.getByText("Google Maps API Key required")).toBeInTheDocument();
  });

  it("keeps the load button disabled until a key is typed", async () => {
    renderWithI18n(<BoroughMap />);
    const button = screen.getByRole("button", { name: "Load map" });
    expect(button).toBeDisabled();
    await userEvent.type(screen.getByPlaceholderText("AIzaSy..."), "test-key");
    expect(button).toBeEnabled();
  });

  it("stores the key in localStorage when it is submitted", async () => {
    renderWithI18n(<BoroughMap />);
    await userEvent.type(screen.getByPlaceholderText("AIzaSy..."), "test-key");
    await userEvent.click(screen.getByRole("button", { name: "Load map" }));
    expect(localStorage.getItem("gmaps_api_key")).toBe("test-key");
  });

  it("shows the prompt in Spanish when the language is Spanish", () => {
    renderWithI18n(<BoroughMap />, "es");
    expect(screen.getByText("Se requiere clave de Google Maps API")).toBeInTheDocument();
  });
});
