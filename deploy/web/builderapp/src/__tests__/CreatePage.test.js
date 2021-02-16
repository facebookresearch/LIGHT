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
import CreatePage from "../components/CreatePage";

describe("<CreatePage />", () => {
	it("initialize on object create form with blank inputs", async () => {
		const fetchSpy = jest.spyOn(global, "fetch").mockResolvedValueOnce({
			json: () => {
				return baseObjects;
			},
		});
		const { getByTestId, getByLabelText } = render(
			<MemoryRouter initialEntries={["/create"]}>
				<CreatePage location={{}} />
			</MemoryRouter>
		);

		expect(getByTestId("header")).toHaveTextContent("Create new entity");

		await wait(() => getByTestId("form"));

		expect(getByLabelText("Name (required)").value).toEqual("");
		expect(getByLabelText("Name Prefix (required)").value).toEqual("");
		expect(getByLabelText("Physical Description (required)").value).toEqual("");
		expect(getByLabelText("Container").checked).toEqual(false);
		expect(getByLabelText("Drink").checked).toEqual(false);
		expect(getByLabelText("Container").checked).toEqual(false);
		expect(getByLabelText("Food").checked).toEqual(false);
		expect(getByLabelText("Gettable").checked).toEqual(false);
		expect(getByLabelText("Plural").checked).toEqual(false);
		expect(getByLabelText("Surface").checked).toEqual(false);
		expect(getByLabelText("Weapon").checked).toEqual(false);
		expect(getByLabelText("Wearable").checked).toEqual(false);
		expect(fetchSpy).toHaveBeenCalledTimes(1);

		fetchSpy.mockClear();
	});

	it("initialize correct create form with correct inputs if state is passed", async () => {
		const fetchSpy = jest.spyOn(global, "fetch").mockResolvedValueOnce({
			json: () => {
				return baseCharacters;
			},
		});
		const { getByTestId, getByLabelText } = render(
			<MemoryRouter initialEntries={["/create"]}>
				<CreatePage
					location={{
						state: {
							entity: {
								id: 1326,
								name: "people escaping the loud city",
								base_id: 1325,
								persona:
									"I live in a large city, but I am leaving it behind.  There is too much noise in this city and I can't take it any more.  I seek to live in the peaceful and more quiet countryside.",
								physical_description:
									"this person loves seclusion and is most at peace in nature",
								name_prefix: "some",
								is_plural: 1.0,
								char_type: "person",
							},
							type: "character",
						},
					}}
				/>
			</MemoryRouter>
		);

		expect(getByTestId("header")).toHaveTextContent("Create new entity");

		expect(getByTestId("radio-character").checked).toEqual(true);

		await wait(() => getByTestId("form"));

		expect(getByLabelText("Name (required)").value).toEqual(
			"people escaping the loud city"
		);
		expect(getByLabelText("Name Prefix (required)").value).toEqual("some");
		expect(getByLabelText("Persona (required)").value).toEqual(
			"I live in a large city, but I am leaving it behind.  There is too much noise in this city and I can't take it any more.  I seek to live in the peaceful and more quiet countryside."
		);
		expect(getByLabelText("Physical Description (required)").value).toEqual(
			"this person loves seclusion and is most at peace in nature"
		);
		expect(getByLabelText("Character Type (required)").value).toEqual("person");
		expect(getByLabelText("Plural").checked).toEqual(true);
		expect(fetchSpy).toHaveBeenCalledTimes(1);

		fetchSpy.mockClear();
	});

	it("can select character type and form becomes a character form", async () => {
		const fetchSpy = jest
			.spyOn(global, "fetch")
			.mockResolvedValueOnce({
				json: () => {
					return baseObjects;
				},
			})
			.mockResolvedValueOnce({
				json: () => {
					return baseCharacters;
				},
			});
		const { getByTestId, getByLabelText } = render(
			<MemoryRouter initialEntries={["/create"]}>
				<CreatePage location={{}} />
			</MemoryRouter>
		);

		await wait(() => getByTestId("form"));

		fireEvent.click(getByTestId("radio-character"), {
			target: { value: "character" },
		});

		await wait(() => getByTestId("form"));

		expect(getByLabelText("Name (required)").value).toEqual("");
		expect(getByLabelText("Name Prefix (required)").value).toEqual("");
		expect(getByLabelText("Persona (required)").value).toEqual("");
		expect(getByLabelText("Physical Description (required)").value).toEqual("");
		expect(getByLabelText("Name Prefix (required)").value).toEqual("");
		expect(getByLabelText("Character Type (required)").value).toEqual("");
		expect(getByLabelText("Plural").checked).toEqual(false);
		expect(fetchSpy).toHaveBeenCalledTimes(2);

		fetchSpy.mockClear();
	});

	it("can select room type and form becomes a room form", async () => {
		const fetchSpy = jest
			.spyOn(global, "fetch")
			.mockResolvedValueOnce({
				json: () => {
					return baseObjects;
				},
			})
			.mockResolvedValueOnce({
				json: () => {
					return baseRooms;
				},
			});
		const { getByTestId, getByLabelText } = render(
			<MemoryRouter initialEntries={["/create"]}>
				<CreatePage location={{}} />
			</MemoryRouter>
		);

		await wait(() => getByTestId("form"));

		fireEvent.click(getByTestId("radio-room"), {
			target: { value: "room" },
		});

		await wait(() => getByTestId("form"));

		expect(getByLabelText("Name (required)").value).toEqual("");
		expect(getByLabelText("Description (required)").value).toEqual("");
		expect(getByLabelText("Backstory (required)").value).toEqual("");
		expect(fetchSpy).toHaveBeenCalledTimes(2);

		fetchSpy.mockClear();
	});

	it("cannot submit object form until all required inputs are filled", async () => {
		const fetchSpy = jest.spyOn(global, "fetch").mockResolvedValueOnce({
			json: () => {
				return baseObjects;
			},
		});
		const { container, getByTestId, getByLabelText } = render(
			<MemoryRouter initialEntries={["/create"]}>
				<CreatePage location={{}} />
			</MemoryRouter>
		);

		expect(getByTestId("header")).toHaveTextContent("Create new entity");

		await wait(() => getByTestId("form"));

		const submitButton = getByText(container, "Save Changes").parentElement;
		expect(submitButton).toBeDisabled();
		fireEvent.change(getByLabelText("Name (required)"), {
			target: { value: "some name" },
		});
		await wait(() => expect(submitButton).toBeDisabled());
		fireEvent.change(getByLabelText("Name Prefix (required)"), {
			target: { value: "some name prefix" },
		});
		await wait(() => expect(submitButton).toBeDisabled());
		fireEvent.change(getByLabelText("Physical Description (required)"), {
			target: { value: "some physical description" },
		});
		await wait(() => expect(submitButton).toBeDisabled());
		fireEvent.focus(getByTestId("base-suggest"));
		await wait(() => getByText(container, "tree"));
		fireEvent.click(getByText(container, "tree"));
		await waitForElementToBeRemoved(() => getByText(container, "tree"));

		expect(submitButton).toBeEnabled();

		fetchSpy.mockClear();
	});

	it("cannot submit character form until all required inputs are filled", async () => {
		const fetchSpy = jest
			.spyOn(global, "fetch")
			.mockResolvedValueOnce({
				json: () => {
					return baseObjects;
				},
			})
			.mockResolvedValueOnce({
				json: () => {
					return baseCharacters;
				},
			});
		const { container, getByTestId, getByLabelText } = render(
			<MemoryRouter initialEntries={["/create"]}>
				<CreatePage location={{}} />
			</MemoryRouter>
		);

		expect(getByTestId("header")).toHaveTextContent("Create new entity");

		await wait(() => getByTestId("form"));

		fireEvent.click(getByTestId("radio-character"), {
			target: { value: "character" },
		});

		await wait(() => getByTestId("form"));

		const submitButton = getByText(container, "Save Changes").parentElement;
		expect(submitButton).toBeDisabled();
		fireEvent.change(getByLabelText("Name (required)"), {
			target: { value: "some name" },
		});
		await wait(() => expect(submitButton).toBeDisabled());
		fireEvent.change(getByLabelText("Name Prefix (required)"), {
			target: { value: "some name prefix" },
		});
		await wait(() => expect(submitButton).toBeDisabled());
		fireEvent.change(getByLabelText("Persona (required)"), {
			target: { value: "some persona" },
		});
		await wait(() => expect(submitButton).toBeDisabled());
		fireEvent.change(getByLabelText("Physical Description (required)"), {
			target: { value: "some physical description" },
		});
		await wait(() => expect(submitButton).toBeDisabled());
		fireEvent.change(getByLabelText("Character Type (required)"), {
			target: { value: "some character type" },
		});
		await wait(() => expect(submitButton).toBeDisabled());
		fireEvent.focus(getByTestId("base-suggest"));
		await wait(() => getByText(container, "animal"));
		fireEvent.click(getByText(container, "animal"));
		await waitForElementToBeRemoved(() => getByText(container, "animal"));

		expect(submitButton).toBeEnabled();

		fetchSpy.mockClear();
	});

	it("cannot submit room form until all required inputs are filled", async () => {
		const fetchSpy = jest
			.spyOn(global, "fetch")
			.mockResolvedValueOnce({
				json: () => {
					return baseObjects;
				},
			})
			.mockResolvedValueOnce({
				json: () => {
					return baseRooms;
				},
			});
		const { container, getByTestId, getByLabelText } = render(
			<MemoryRouter initialEntries={["/create"]}>
				<CreatePage location={{}} />
			</MemoryRouter>
		);

		expect(getByTestId("header")).toHaveTextContent("Create new entity");

		await wait(() => getByTestId("form"));

		fireEvent.click(getByTestId("radio-room"), {
			target: { value: "room" },
		});

		await wait(() => getByTestId("form"));

		const submitButton = getByText(container, "Save Changes").parentElement;
		expect(submitButton).toBeDisabled();
		fireEvent.change(getByLabelText("Name (required)"), {
			target: { value: "some name" },
		});
		await wait(() => expect(submitButton).toBeDisabled());
		fireEvent.change(getByLabelText("Description (required)"), {
			target: { value: "some description" },
		});
		await wait(() => expect(submitButton).toBeDisabled());
		fireEvent.change(getByLabelText("Backstory (required)"), {
			target: { value: "some backstory" },
		});
		await wait(() => expect(submitButton).toBeDisabled());
		fireEvent.focus(getByTestId("base-suggest"));
		await wait(() => getByText(container, "Inside Church"));
		fireEvent.click(getByText(container, "Inside Church"));
		await waitForElementToBeRemoved(() =>
			getByText(container, "Inside Church")
		);

		expect(submitButton).toBeEnabled();

		fetchSpy.mockClear();
	});
});

const baseObjects = [
	{ id: 5008, name: "tree" },
	{ id: 5010, name: "equipment" },
	{ id: 5012, name: "clothing" },
];

const baseCharacters = [
	{ id: 1323, name: "animal" },
	{ id: 1325, name: "people" },
	{ id: 1327, name: "person" },
	{ id: 1335, name: "rabbit" },
];

const baseRooms = [
	{ id: 1, name: "Inside Church" },
	{ id: 3, name: "Cave" },
];
