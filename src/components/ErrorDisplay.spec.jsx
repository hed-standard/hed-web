import React from "react";
import { act } from "react";
import { createRoot } from "react-dom/client";
import { ErrorDisplay } from "./ErrorDisplay";

describe("ErrorDisplay", () => {
  let container;
  let root;

  beforeEach(() => {
    container = document.createElement("div");
    document.body.appendChild(container);
  });

  afterEach(() => {
    act(() => root.unmount());
    document.body.removeChild(container);
  });

  async function renderComponent(ui) {
    await act(async () => {
      root = createRoot(container);
      root.render(ui);
    });
  }

  it("shows no-issues message when errors is empty", async () => {
    await renderComponent(<ErrorDisplay errors={[]} />);
    expect(container.textContent).toContain("No validation issues found.");
  });

  it("shows no-issues message when errors is null", async () => {
    await renderComponent(<ErrorDisplay errors={null} />);
    expect(container.textContent).toContain("No validation issues found.");
  });

  it("shows validation issues when errors are provided", async () => {
    const errors = [{ message: "TEST_ERROR", severity: "error" }];
    await renderComponent(
      <ErrorDisplay errors={errors} downloadableErrors={errors} />
    );
    expect(container.textContent).toContain("Validation Issues Found");
  });
});
