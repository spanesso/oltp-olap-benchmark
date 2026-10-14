import { describe, it, expect, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { I18nProvider, useI18n } from "../../src/i18n";
import { en } from "../../src/i18n/translations/en";
import { es } from "../../src/i18n/translations/es";
import { LanguageToggle } from "../../src/presentation/components/LanguageToggle";

function Probe() {
  const { lang, t } = useI18n();
  return (
    <p>
      {lang}: {t("stat_queries")}
    </p>
  );
}

beforeEach(() => {
  localStorage.clear();
});

describe("I18nProvider", () => {
  it("defaults to Spanish", () => {
    render(
      <I18nProvider>
        <Probe />
      </I18nProvider>,
    );
    expect(screen.getByText("es: Queries")).toBeInTheDocument();
  });

  it("restores the language stored in localStorage", () => {
    localStorage.setItem("bench_lang", "en");
    render(
      <I18nProvider>
        <Probe />
      </I18nProvider>,
    );
    expect(screen.getByText("en: Queries")).toBeInTheDocument();
  });

  it("ignores an invalid stored language", () => {
    localStorage.setItem("bench_lang", "fr");
    render(
      <I18nProvider>
        <Probe />
      </I18nProvider>,
    );
    expect(screen.getByText(/^es:/)).toBeInTheDocument();
  });

  it("switches language from the toggle and persists the choice", async () => {
    render(
      <I18nProvider>
        <LanguageToggle />
        <Probe />
      </I18nProvider>,
    );
    await userEvent.click(screen.getByRole("button", { name: "EN" }));
    expect(screen.getByText(/^en:/)).toBeInTheDocument();
    expect(localStorage.getItem("bench_lang")).toBe("en");
  });

  it("throws when used outside the provider", () => {
    expect(() => render(<Probe />)).toThrow("useI18n must be used inside I18nProvider");
  });
});

describe("translations", () => {
  it("define the same keys in English and Spanish", () => {
    expect(Object.keys(es).sort()).toEqual(Object.keys(en).sort());
  });

  it("have no empty values", () => {
    for (const dict of [en, es]) {
      for (const [key, value] of Object.entries(dict)) {
        expect(value, key).not.toBe("");
      }
    }
  });
});
