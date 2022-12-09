/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import "@testing-library/jest-dom/extend-expect";
import React from "react";
import { MemoryRouter } from "react-router-dom";
import {
  getByText,
  render,
  fireEvent,
  wait,
  waitForElementToBeRemoved,
} from "@testing-library/react";
import EditPage from "../components/EditPage";

describe("<EditPage />", () => {
  it("loads object entity data to form", async () => {
    const fetchSpy = jest
      .spyOn(global, "fetch")
      .mockResolvedValueOnce({
        json: () => {
          return object;
        },
      })
      .mockResolvedValueOnce({
        json: () => {
          return baseObjects;
        },
      });
    const { container, getByTestId, getByLabelText } = render(
      <MemoryRouter initialEntries={["/create"]}>
        <EditPage match={{ params: { id: 5009 } }} location={{}} />
      </MemoryRouter>
    );

    expect(container.querySelector(".bp3-spinner")).toBeInTheDocument();
    expect(getByTestId("header")).toHaveTextContent("Editing Entity 5009");

    await wait(() => getByTestId("form"));

    expect(getByLabelText("Name (required)").value).toEqual(
      "towering pine trees"
    );
    expect(getByLabelText("Name Prefix (required)").value).toEqual("some");
    expect(getByLabelText("Physical Description (required)").value).toEqual(
      "the tree is tall and leafy"
    );
    expect(getByLabelText("Container").checked).toEqual(false);
    expect(getByLabelText("Drink").checked).toEqual(false);
    expect(getByLabelText("Container").checked).toEqual(false);
    expect(getByLabelText("Food").checked).toEqual(false);
    expect(getByLabelText("Gettable").checked).toEqual(true);
    expect(getByLabelText("Plural").checked).toEqual(true);
    expect(getByLabelText("Surface").checked).toEqual(false);
    expect(getByLabelText("Weapon").checked).toEqual(false);
    expect(getByLabelText("Wearable").checked).toEqual(false);
    expect(fetchSpy).toHaveBeenCalledTimes(2);
    expect(fetchSpy.mock.calls[0][0]).toContain("/entities/5009");

    fetchSpy.mockClear();
  });

  it("loads character entity data to form", async () => {
    const fetchSpy = jest
      .spyOn(global, "fetch")
      .mockResolvedValueOnce({
        json: () => {
          return character;
        },
      })
      .mockResolvedValueOnce({
        json: () => {
          return baseCharacters;
        },
      });
    const { container, getByTestId, getByLabelText } = render(
      <MemoryRouter initialEntries={["/create"]}>
        <EditPage match={{ params: { id: 1324 } }} location={{}} />
      </MemoryRouter>
    );

    expect(container.querySelector(".bp3-spinner")).toBeInTheDocument();
    expect(getByTestId("header")).toHaveTextContent("Editing Entity 1324");

    await wait(() => getByTestId("form"));

    expect(getByLabelText("Name (required)").value).toEqual("other animals");
    expect(getByLabelText("Name Prefix (required)").value).toEqual("some");
    expect(getByLabelText("Persona (required)").value).toEqual(
      "I am one of the other animals that lives in the meadow surrounding the castle. I play with the other animals all day. I'm only frightened when fighting breaks out in the meadow or forest."
    );
    expect(getByLabelText("Physical Description (required)").value).toEqual(
      "A friendly and playful beast that roams the sprawling meadow surrounding the castle."
    );
    expect(getByLabelText("Character Type (required)").value).toEqual("person");
    expect(getByLabelText("Plural").checked).toEqual(true);
    expect(fetchSpy).toHaveBeenCalledTimes(2);
    expect(fetchSpy.mock.calls[0][0]).toContain("/entities/1324");

    fetchSpy.mockClear();
  });

  it("loads room entity data to form", async () => {
    const fetchSpy = jest
      .spyOn(global, "fetch")
      .mockResolvedValueOnce({
        json: () => {
          return room;
        },
      })
      .mockResolvedValueOnce({
        json: () => {
          return baseRooms;
        },
      });
    const { container, getByTestId, getByLabelText } = render(
      <MemoryRouter initialEntries={["/create"]}>
        <EditPage match={{ params: { id: 2 } }} location={{}} />
      </MemoryRouter>
    );

    expect(container.querySelector(".bp3-spinner")).toBeInTheDocument();
    expect(getByTestId("header")).toHaveTextContent("Editing Entity 2");

    await wait(() => getByTestId("form"));

    expect(getByLabelText("Name (required)").value).toEqual("The rectory");
    expect(getByLabelText("Backstory (required)").value).toEqual(
      "The rectory is one of the most important rooms in the church, as it is where the priest and others get ready before they start church, where the put on robes and cassocks and the like. It is vital to the church as a matter of fact. Visibility to the room is blocked off by the altar in front of it, so church goers cannot see it unless they walk behind the altar. It seems to be used as a bit of a storage area for religious artifacts."
    );
    expect(getByLabelText("Description (required)").value).toEqual(
      "This room is quite small and cramped. It's about the size of maybe three wooden carts, which is to say, it's very small. There are boxes all over the place and many candles and other church accessories. There are several big robes hanging next to what looks like a very small closet. Some candles shed an eerie light on the room, flickering softly. There is a small cabinet with several religious tapes and records and a few books. A book case is near and contains many common religious texts."
    );
    expect(fetchSpy).toHaveBeenCalledTimes(2);
    expect(fetchSpy.mock.calls[0][0]).toContain("/entities/2");

    fetchSpy.mockClear();
  });

  it("should popup confirmation dialog with edits before submitting edits", async () => {
    jest
      .spyOn(global, "fetch")
      .mockResolvedValueOnce({
        json: () => {
          return object;
        },
      })
      .mockResolvedValueOnce({
        json: () => {
          return baseObjects;
        },
      });
    const { container, getByTestId, getByLabelText } = render(
      <MemoryRouter initialEntries={["/create"]}>
        <EditPage match={{ params: { id: 5009 } }} location={{}} />
      </MemoryRouter>
    );

    await wait(() => getByTestId("form"));

    const nameInput = getByLabelText("Name (required)");

    fireEvent.change(nameInput, { target: { value: "some name" } });
    fireEvent.click(getByText(container, "Save Changes"));
    await wait(() => getByText(container, "Confirm edits for Entity 5009"));
    const dialog = container.querySelector(".bp3-dialog");

    expect(dialog.querySelector("p").textContent).toEqual("name: some name");
  });

  describe("<ObjectForm />", () => {
    it("validates form correctly", async () => {
      jest
        .spyOn(global, "fetch")
        .mockResolvedValueOnce({
          json: () => {
            return object;
          },
        })
        .mockResolvedValueOnce({
          json: () => {
            return baseObjects;
          },
        });
      const { container, getByTestId, getByLabelText, findByText } = render(
        <MemoryRouter initialEntries={["/create"]}>
          <EditPage match={{ params: { id: 5009 } }} location={{}} />
        </MemoryRouter>
      );

      await wait(() => getByTestId("form"));

      const nameInput = getByLabelText("Name (required)");
      fireEvent.change(nameInput, { target: { value: "" } });
      fireEvent.blur(nameInput);
      const error = await findByText("Required");

      expect(error).toHaveClass("form-error");
      expect(nameInput.parentElement).toHaveClass("bp3-intent-danger");
      expect(getByText(container, "Save Changes")).toBeDisabled();
      expect(getByText(container, "Reset")).toBeEnabled();

      fireEvent.change(nameInput, { target: { value: "some name" } });
      fireEvent.blur(nameInput);

      await waitForElementToBeRemoved(() => getByText(container, "Required"));

      expect(getByText(container, "Save Changes")).toBeEnabled();
    });
  });

  describe("<CharacterForm />", () => {
    it("validates form correctly", async () => {
      jest
        .spyOn(global, "fetch")
        .mockResolvedValueOnce({
          json: () => {
            return character;
          },
        })
        .mockResolvedValueOnce({
          json: () => {
            return baseCharacters;
          },
        });
      const { container, getByTestId, getByLabelText, findByText } = render(
        <MemoryRouter initialEntries={["/create"]}>
          <EditPage match={{ params: { id: 1324 } }} location={{}} />
        </MemoryRouter>
      );

      await wait(() => getByTestId("form"));

      const nameInput = getByLabelText("Name (required)");
      fireEvent.change(nameInput, { target: { value: "" } });
      fireEvent.blur(nameInput);
      const error = await findByText("Required");

      expect(error).toHaveClass("form-error");
      expect(nameInput.parentElement).toHaveClass("bp3-intent-danger");
      expect(getByText(container, "Save Changes")).toBeDisabled();
      expect(getByText(container, "Reset")).toBeEnabled();

      fireEvent.change(nameInput, { target: { value: "some name" } });
      fireEvent.blur(nameInput);

      await waitForElementToBeRemoved(() => getByText(container, "Required"));

      expect(getByText(container, "Save Changes")).toBeEnabled();
    });
  });

  describe("<RoomForm />", () => {
    it("validates form correctly", async () => {
      jest
        .spyOn(global, "fetch")
        .mockResolvedValueOnce({
          json: () => {
            return room;
          },
        })
        .mockResolvedValueOnce({
          json: () => {
            return baseRooms;
          },
        });
      const { container, getByTestId, getByLabelText, findByText } = render(
        <MemoryRouter initialEntries={["/create"]}>
          <EditPage match={{ params: { id: 2 } }} location={{}} />
        </MemoryRouter>
      );

      await wait(() => getByTestId("form"));

      const nameInput = getByLabelText("Name (required)");
      fireEvent.change(nameInput, { target: { value: "" } });
      fireEvent.blur(nameInput);
      const error = await findByText("Required");

      expect(error).toHaveClass("form-error");
      expect(nameInput.parentElement).toHaveClass("bp3-intent-danger");
      expect(getByText(container, "Save Changes")).toBeDisabled();
      expect(getByText(container, "Reset")).toBeEnabled();

      fireEvent.change(nameInput, { target: { value: "some name" } });
      fireEvent.blur(nameInput);

      await waitForElementToBeRemoved(() => getByText(container, "Required"));

      expect(getByText(container, "Save Changes")).toBeEnabled();
    });
  });
});

const object = {
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
    is_plural: 1.0,
  },
  type: "object",
};

const baseObjects = [
  { id: 5008, name: "tree" },
  { id: 5010, name: "equipment" },
  { id: 5012, name: "clothing" },
];

const character = {
  entity: {
    id: 1324,
    name: "other animals",
    base_id: 1323,
    persona:
      "I am one of the other animals that lives in the meadow surrounding the castle. I play with the other animals all day. I'm only frightened when fighting breaks out in the meadow or forest.",
    physical_description:
      "A friendly and playful beast that roams the sprawling meadow surrounding the castle.",
    name_prefix: "some",
    is_plural: 1.0,
    char_type: "person",
  },
  type: "character",
};

const baseCharacters = [
  { id: 1323, name: "animal" },
  { id: 1325, name: "people" },
  { id: 1327, name: "person" },
  { id: 1335, name: "rabbit" },
];

const room = {
  entity: {
    id: 2,
    name: "The rectory",
    base_id: 1,
    description:
      "This room is quite small and cramped. It's about the size of maybe three wooden carts, which is to say, it's very small. There are boxes all over the place and many candles and other church accessories. There are several big robes hanging next to what looks like a very small closet. Some candles shed an eerie light on the room, flickering softly. There is a small cabinet with several religious tapes and records and a few books. A book case is near and contains many common religious texts.",
    backstory:
      "The rectory is one of the most important rooms in the church, as it is where the priest and others get ready before they start church, where the put on robes and cassocks and the like. It is vital to the church as a matter of fact. Visibility to the room is blocked off by the altar in front of it, so church goers cannot see it unless they walk behind the altar. It seems to be used as a bit of a storage area for religious artifacts.",
  },
  type: "room",
};

const baseRooms = [
  { id: 1, name: "Inside Church" },
  { id: 3, name: "Cave" },
];
