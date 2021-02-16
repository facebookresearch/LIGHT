import "@testing-library/jest-dom/extend-expect";
import React from "react";
import { MemoryRouter } from "react-router-dom";
import {
	getByText,
	getAllByText,
	render,
	fireEvent,
	wait,
} from "@testing-library/react";
import ExplorePage from "../components/ExplorePage";

describe("<ExplorePage />", () => {
	it("renders explore page and loads objects into table", async () => {
		const fetchSpy = jest.spyOn(global, "fetch").mockResolvedValue({
			json: () => {
				return objects;
			},
		});
		const { container, getByTestId, getAllByTestId } = render(
			<MemoryRouter>
				<ExplorePage />
			</MemoryRouter>
		);

		expect(container.querySelector(".bp3-spinner")).toBeInTheDocument();
		expect(getByTestId("header")).toHaveTextContent("Explore");

		await wait(() => getByTestId("table-explore"));

		expect(getAllByTestId("tr-explore").length).toEqual(3);
		expect(fetchSpy).toHaveBeenCalledTimes(1);
		expect(fetchSpy.mock.calls[0][0]).toContain("/entities/object?search=");

		fetchSpy.mockClear();
	});

	it("loads characters into table on radio button selection", async () => {
		const fetchSpy = jest
			.spyOn(global, "fetch")
			.mockResolvedValueOnce({
				json: () => {
					return objects;
				},
			})
			.mockResolvedValueOnce({
				json: () => {
					return characters;
				},
			});
		const { getByTestId, getAllByTestId } = render(
			<MemoryRouter>
				<ExplorePage />
			</MemoryRouter>
		);
		await wait(() => getByTestId("table-explore"));

		expect(getAllByTestId("tr-explore").length).toEqual(3);

		fireEvent.click(getByTestId("radio-character"), {
			target: { value: "character" },
		});
		await wait(() => getByTestId("table-explore"));

		expect(getAllByTestId("tr-explore").length).toEqual(2);
		expect(fetchSpy).toHaveBeenCalledTimes(2);
		expect(fetchSpy.mock.calls[1][0]).toContain("/entities/character?search=");

		fetchSpy.mockClear();
	});

	it("loads rooms into table on radio button selection", async () => {
		const fetchSpy = jest
			.spyOn(global, "fetch")
			.mockResolvedValueOnce({
				json: () => {
					return objects;
				},
			})
			.mockResolvedValueOnce({
				json: () => {
					return rooms;
				},
			});
		const { getByTestId, getAllByTestId } = render(
			<MemoryRouter>
				<ExplorePage />
			</MemoryRouter>
		);
		await wait(() => getByTestId("table-explore"));

		expect(getAllByTestId("tr-explore").length).toEqual(3);

		fireEvent.click(getByTestId("radio-character"), {
			target: { value: "room" },
		});
		await wait(() => getByTestId("table-explore"));

		expect(getAllByTestId("tr-explore").length).toEqual(1);
		expect(fetchSpy).toHaveBeenCalledTimes(2);
		expect(fetchSpy.mock.calls[1][0]).toContain("/entities/room?search=");

		fetchSpy.mockClear();
	});

	it("Clicking on a row will drop down a card with entity info and actions", async () => {
		const fetchSpy = jest.spyOn(global, "fetch").mockResolvedValueOnce({
			json: () => {
				return objects;
			},
		});
		const { container, getByTestId } = render(
			<MemoryRouter>
				<ExplorePage />
			</MemoryRouter>
		);
		await wait(() => getByTestId("table-explore"));
		fireEvent.click(getByText(container, "towering pine trees"));
		await wait(() => getByTestId("dropdown"));

		const dropdown = getByTestId("dropdown");
		expect(getAllByText(dropdown, "Physical Description").length).toEqual(1);
		expect(getAllByText(dropdown, "Name").length).toEqual(1);
		expect(getAllByText(dropdown, ": 5008").length).toEqual(1);
		expect(getAllByText(dropdown, ": some").length).toEqual(1);

		fetchSpy.mockClear();
	});

	it("edit link links to correct edit page", async () => {
		const fetchSpy = jest.spyOn(global, "fetch").mockResolvedValue({
			json: () => {
				return objects;
			},
		});
		const { container, getByTestId } = render(
			<MemoryRouter>
				<ExplorePage />
			</MemoryRouter>
		);
		await wait(() => getByTestId("table-explore"));
		fireEvent.click(getByText(container, "towering pine trees"));
		await wait(() => getByTestId("dropdown"));

		expect(
			getByText(getByTestId("dropdown").parentElement, "Edit").getAttribute(
				"href"
			)
		).toStrictEqual("/edit/5009");

		fetchSpy.mockClear();
	});

	it("Create From link links to create page", async () => {
		const fetchSpy = jest.spyOn(global, "fetch").mockResolvedValue({
			json: () => {
				return objects;
			},
		});
		const { container, getByTestId } = render(
			<MemoryRouter>
				<ExplorePage />
			</MemoryRouter>
		);
		await wait(() => getByTestId("table-explore"));
		fireEvent.click(getByText(container, "towering pine trees"));
		await wait(() => getByTestId("dropdown"));

		expect(
			getByText(
				getByTestId("dropdown").parentElement,
				"Create From"
			).getAttribute("href")
		).toStrictEqual("/create");

		fetchSpy.mockClear();
	});

	it("can navigate through pages", async () => {
		const fetchSpy = jest
			.spyOn(global, "fetch")
			.mockResolvedValueOnce({
				json: () => {
					return characters;
				},
			})
			.mockResolvedValueOnce({
				json: () => {
					return characters;
				},
			});
		const { container, getByTestId } = render(
			<MemoryRouter>
				<ExplorePage />
			</MemoryRouter>
		);

		expect(container.querySelector(".bp3-spinner")).toBeInTheDocument();
		expect(getByTestId("header")).toHaveTextContent("Explore");

		await wait(() => getByTestId("table-explore"));

		fireEvent.click(getByText(container, "next"));
		await wait(() => getByTestId("table-explore"));

		expect(fetchSpy).toHaveBeenCalledTimes(2);
		expect(fetchSpy.mock.calls[0][0]).toContain("page=0");
		expect(fetchSpy.mock.calls[1][0]).toContain("page=1");

		fetchSpy.mockClear();
	});
});

const objects = {
	page: 0,
	per_page: 30,
	total: 3,
	total_pages: 1,
	data: [
		{
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
		{
			id: 5011,
			name: "long skinny trees",
			base_id: 5008,
			is_container: 0.0,
			is_drink: 0.0,
			is_food: 0.0,
			is_gettable: 0.0,
			is_surface: 0.0,
			is_wearable: 0.0,
			is_weapon: 0.0,
			physical_description:
				"the tree has so tall and skinny it was as if it almost couldn't be seen",
			name_prefix: "some",
			is_plural: 1.0,
		},
		{
			id: 5013,
			name: "pine needles",
			base_id: 5012,
			is_container: 0.0,
			is_drink: 0.0,
			is_food: 0.0,
			is_gettable: 1.0,
			is_surface: 0.0,
			is_wearable: 0.0,
			is_weapon: 1.0,
			physical_description: "the needle is sharp and picky.",
			name_prefix: "some",
			is_plural: 1.0,
		},
	],
};

const characters = {
	page: 0,
	per_page: 2,
	total: 2,
	total_pages: 2,
	data: [
		{
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
		{
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
	],
};

const rooms = {
	page: 0,
	per_page: 30,
	total: 1,
	total_pages: 1,
	data: [
		{
			id: 2,
			name: "The rectory",
			base_id: 1,
			description:
				"This room is quite small and cramped. It's about the size of maybe three wooden carts, which is to say, it's very small. There are boxes all over the place and many candles and other church accessories. There are several big robes hanging next to what looks like a very small closet. Some candles shed an eerie light on the room, flickering softly. There is a small cabinet with several religious tapes and records and a few books. A book case is near and contains many common religious texts.",
			backstory:
				"The rectory is one of the most important rooms in the church, as it is where the priest and others get ready before they start church, where the put on robes and cassocks and the like. It is vital to the church as a matter of fact. Visibility to the room is blocked off by the altar in front of it, so church goers cannot see it unless they walk behind the altar. It seems to be used as a bit of a storage area for religious artifacts.",
		},
	],
};
