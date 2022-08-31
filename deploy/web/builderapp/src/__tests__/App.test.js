
/*****
 * Copyright (c) Meta Platforms, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import "@testing-library/jest-dom/extend-expect";
import React from "react";
import { MemoryRouter } from "react-router-dom";
import { render, fireEvent } from "@testing-library/react";
import App, { Routes } from "../App";

describe("<App />", () => {
  it("renders explore page at root", async () => {
    const { getByTestId } = render(
      <MemoryRouter initialEntries={["/"]}>
        <Routes />
      </MemoryRouter>
    );
    expect(getByTestId("header")).toHaveTextContent("Explore");
  });

  it("renders create page at /create", () => {
    const { getByTestId } = render(
      <MemoryRouter initialEntries={["/create"]}>
        <Routes />
      </MemoryRouter>
    );
    expect(getByTestId("header")).toHaveTextContent("Create new entity");
  });

  it("renders review page at /review", () => {
    const { getByTestId } = render(
      <MemoryRouter initialEntries={["/review"]}>
        <Routes />
      </MemoryRouter>
    );
    expect(getByTestId("header")).toHaveTextContent("Review");
  });

  it("renders edit page at /edit/:id", () => {
    const { getByTestId } = render(
      <MemoryRouter initialEntries={["/edit/1"]}>
        <Routes />
      </MemoryRouter>
    );
    expect(getByTestId("header")).toHaveTextContent("Editing Entity 1");
  });

  describe("Navbar should navigate to", () => {
    it("Create Page", () => {
      const { getByTestId } = render(<App />);
      fireEvent.click(getByTestId("link-create"));
      expect(getByTestId("header")).toHaveTextContent("Create new entity");
    });

    it("Review Page", () => {
      const { getByTestId } = render(<App />);
      fireEvent.click(getByTestId("link-review"));
      expect(getByTestId("header")).toHaveTextContent("Review");
    });

    it("Explore Page", () => {
      const { getByTestId } = render(<App />);
      fireEvent.click(getByTestId("link-create"));
      fireEvent.click(getByTestId("link-explore"));
      expect(getByTestId("header")).toHaveTextContent("Explore");
    });
  });
});
