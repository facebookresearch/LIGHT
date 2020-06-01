import "@testing-library/jest-dom/extend-expect";
import React from "react";
import {
  getByText,
  getAllByText,
  render,
  fireEvent,
  wait
} from "@testing-library/react";

import ReviewPage from "../components/ReviewPage";
import * as utils from "../utils";

describe("<ReviewPage />", () => {
  it("renders review page and loads pending edits into table", async () => {
    const fetchSpy = jest.spyOn(global, "fetch").mockResolvedValue({
      json: () => {
        return edits;
      }
    });
    const { container, getByTestId, getAllByTestId } = render(<ReviewPage />);

    expect(container.querySelector(".bp3-spinner")).toBeInTheDocument();
    expect(getByTestId("header")).toHaveTextContent("Review");

    await wait(() => getByTestId("table-review"));

    expect(getAllByTestId("tr-review").length).toEqual(3);
    expect(fetchSpy).toHaveBeenCalledTimes(1);
    expect(fetchSpy.mock.calls[0][0]).toContain(
      "/edits?expand=true&status=under review"
    );

    fetchSpy.mockClear();
  });

  it("loads accepted edits into table on radio button selection", async () => {
    const fetchSpy = jest
      .spyOn(global, "fetch")
      .mockResolvedValueOnce({
        json: () => {
          return edits;
        }
      })
      .mockResolvedValueOnce({
        json: () => {
          return accepted;
        }
      });
    const { getByTestId, getAllByTestId } = render(<ReviewPage />);
    await wait(() => getByTestId("table-review"));

    expect(getAllByTestId("tr-review").length).toEqual(3);

    fireEvent.click(getByTestId("radio-accepted"), {
      target: { value: "accepted" }
    });
    await wait(() => getByTestId("table-review"));

    expect(getAllByTestId("tr-review").length).toEqual(1);
    expect(fetchSpy).toHaveBeenCalledTimes(2);
    expect(fetchSpy.mock.calls[1][0]).toContain(
      "/edits?expand=true&status=accepted"
    );

    fetchSpy.mockClear();
  });

  it("loads rejected edits into table on radio button selection", async () => {
    const fetchSpy = jest
      .spyOn(global, "fetch")
      .mockResolvedValueOnce({
        json: () => {
          return edits;
        }
      })
      .mockResolvedValueOnce({
        json: () => {
          return rejected;
        }
      });
    const { getByTestId, getAllByTestId } = render(<ReviewPage />);
    await wait(() => getByTestId("table-review"));

    expect(getAllByTestId("tr-review").length).toEqual(3);

    fireEvent.click(getByTestId("radio-rejected"), {
      target: { value: "rejected" }
    });
    await wait(() => getByTestId("table-review"));

    expect(getAllByTestId("tr-review").length).toEqual(2);
    expect(fetchSpy).toHaveBeenCalledTimes(2);
    expect(fetchSpy.mock.calls[1][0]).toContain(
      "/edits?expand=true&status=rejected"
    );

    fetchSpy.mockClear();
  });

  describe("Pending Edit flow", () => {
    let fetchSpy;
    let postSpy;
    beforeEach(() => {
      postSpy = jest.spyOn(utils, "post").mockResolvedValue({
        json: () => {
          return {};
        }
      });

      fetchSpy = jest.spyOn(global, "fetch").mockResolvedValueOnce({
        json: () => {
          return edits;
        }
      });
    });
    afterEach(async () => {
      fetchSpy.mockClear();
      postSpy.mockClear();
    });
    it("Clicking on a row will drop down a card with entity info", async () => {
      fetchSpy = fetchSpy.mockResolvedValueOnce({
        json: () => {
          return entity;
        }
      });
      const { container, getByTestId } = render(<ReviewPage />);
      await wait(() => getByTestId("table-review"));
      fireEvent.click(getByText(container, "is_food"));
      await wait(() => getByTestId("dropdown"));

      expect(
        getAllByText(getByTestId("dropdown"), "Physical Description").length
      ).toEqual(2);
      expect(getAllByText(getByTestId("dropdown"), "Name").length).toEqual(2);
      expect(fetchSpy.mock.calls[1][0]).toContain("/entities/5011");
    });

    it("Clicking the accept button in the drop down will accept the edit", async () => {
      fetchSpy = fetchSpy.mockResolvedValueOnce({
        json: () => {
          return entity;
        }
      });
      const { container, getByTestId } = render(<ReviewPage />);
      await wait(() => getByTestId("table-review"));
      fireEvent.click(getByText(container, "is_food"));
      await wait(() => getByTestId("dropdown"));
      fireEvent.click(getByText(container, "Accept Edit"));
      await wait(() => container.querySelector(".bp3-spinner"));

      expect(postSpy).toHaveBeenCalledTimes(1);
      expect(postSpy.mock.calls[0][0]).toContain("edits/1/accept/accepted");
    });

    it("Checking any checkboxes will enable accept/reject buttons and all selected will be submitted", async () => {
      fetchSpy = fetchSpy.mockResolvedValueOnce({
        json: () => {
          return [];
        }
      });
      const { container, getByTestId, getAllByRole } = render(<ReviewPage />);
      await wait(() => getByTestId("table-review"));

      expect(getByText(container, "Accept")).toBeDisabled();
      expect(getByText(container, "Reject")).toBeDisabled();

      const checkboxes = getAllByRole("checkbox");

      expect(checkboxes.length).toEqual(4);

      fireEvent.click(checkboxes[1]);

      expect(getByText(container, "Accept")).toBeEnabled();
      expect(getByText(container, "Reject")).toBeEnabled();

      fireEvent.click(checkboxes[0]);

      expect(getByText(container, "Accept")).toBeDisabled();
      expect(getByText(container, "Reject")).toBeDisabled();
      expect(checkboxes[1].checked).toEqual(false);
      expect(checkboxes[2].checked).toEqual(false);
      expect(checkboxes[3].checked).toEqual(false);

      fireEvent.click(checkboxes[0]);

      expect(checkboxes[1].checked).toEqual(true);
      expect(checkboxes[2].checked).toEqual(true);
      expect(checkboxes[3].checked).toEqual(true);

      fireEvent.click(getAllByText(container, "Accept")[0]);

      expect(
        getByText(container, "Confirm edits to be accepted")
      ).toBeInTheDocument();

      fireEvent.click(getAllByText(container, "Confirm Edits")[0]);

      await wait(() => container.querySelector(".bp3-spinner"));

      expect(postSpy).toHaveBeenCalledTimes(3);
      expect(postSpy.mock.calls[0][0]).toContain("edits/1/accept/accepted");
      expect(postSpy.mock.calls[1][0]).toContain("edits/2/accept/accepted");
      expect(postSpy.mock.calls[2][0]).toContain("edits/3/accept/accepted");
    });
  });
});

const edits = [
  {
    edit_id: 1,
    id: 5011,
    field: "is_food",
    unedited_value: "0.0",
    edited_value: "1",
    player_id: 1,
    status: "under review",
    type: "object",
    base: "tree"
  },
  {
    edit_id: 2,
    id: 5025,
    field: "is_drink",
    unedited_value: "0.0",
    edited_value: "1",
    player_id: 1,
    status: "under review",
    type: "object",
    base: "sail"
  },
  {
    edit_id: 3,
    id: 5025,
    field: "is_container",
    unedited_value: "0.0",
    edited_value: "1",
    player_id: 1,
    status: "under review",
    type: "object",
    base: "sail"
  }
];

const accepted = [
  {
    edit_id: 43,
    id: 5013,
    field: "name_prefix",
    unedited_value: "some",
    edited_value: "dasd",
    player_id: 1,
    status: "accepted",
    type: "object",
    base: "needle"
  }
];

const rejected = [
  {
    edit_id: 6,
    id: 5013,
    field: "is_container",
    unedited_value: "0.0",
    edited_value: "true",
    player_id: 1,
    status: "rejected",
    type: "object",
    base: "needle"
  },
  {
    edit_id: 7,
    id: 5011,
    field: "is_container",
    unedited_value: "0.0",
    edited_value: "true",
    player_id: 1,
    status: "rejected",
    type: "object",
    base: "tree"
  }
];

const entity = {
  entity: {
    id: 5009,
    name: "towering pine trees",
    base_id: 5008,
    is_container: 0.0,
    is_drink: 0.0,
    is_food: 0.0,
    is_gettable: 1.0,
    is_surface: 0.0,
    is_wearable: 0.0,
    is_weapon: 0.0,
    physical_description: "the tree is tall and leafy",
    name_prefix: "some",
    is_plural: 1.0
  },
  type: "object"
};
