import React from "react";
import { Formik } from "formik";
import {
	Button,
	Intent,
	Icon,
	Popover,
	PopoverInteractionKind,
	Tooltip,
} from "@blueprintjs/core";
import { isEmpty, cloneDeep } from "lodash";
import AnimateHeight from "react-animate-height";
import { Picker } from "emoji-mart";
import "emoji-mart/css/emoji-mart.css";

import ColorPicker from "./ColorPicker";
import BaseSuggest from "./BaseSuggest";
import BaseMultiSelect from "./BaseMultiSelect";
import {
	TILE_COLORS,
	findBiome,
	invertColor,
	findEmoji,
	DEFAULT_EMOJI,
} from "../worldbuilding/utils";
import ObjectForm, { emptyObjectForm } from "./ObjectForm";
import CharacterForm, { emptyCharacterForm } from "./CharacterForm";
import RoomForm, { emptyRoomForm } from "./RoomForm";
import { emptyTileForm } from "./TileForm";

/**
 * Advanced tile editing options including creating, editing, and duplicating entities
 */
function AdvancedTileForm({
	x,
	y,
	currFloor,
	getTileAt,
	initialInputs,
	inheritedInputs,
	handleSubmit,
	handleClear,
	tileStyle,
	entities,
	findOrAddEntity,
	editEntity,
}) {
	const TilePreview = ({ tile }) => {
		const contentColor = invertColor(
			tile && !isNaN(tile.room) && tile.color ? tile.color : "#ced9e0"
		);
		return (
			<div style={{ display: "flex", justifyContent: "center" }}>
				<div
					style={{
						position: "relative",
					}}
				>
					<Icon
						color={contentColor}
						className={`react-grid-item-handle + ${
							isNaN(tile.room) ? "disabled" : ""
						}`}
						icon="drag-handle-horizontal"
					/>
					{!isEmpty(tile) && !isEmpty(getTileAt(x, y, currFloor - 1)) && (
						<Icon
							color={contentColor}
							className={isEmpty(tile) ? "disabled" : ""}
							style={{
								opacity: tile.stairDown ? 1 : 0.2,
								position: "absolute",
								bottom: "5px",
								left: "5px",
							}}
							icon="arrow-bottom-left"
						/>
					)}
					{!isEmpty(tile) && !isEmpty(getTileAt(x, y, currFloor + 1)) && (
						<Icon
							color={contentColor}
							className={isEmpty(tile) ? "disabled" : ""}
							style={{
								opacity: tile.stairUp ? 1 : 0.2,
								position: "absolute",
								top: "5px",
								right: "5px",
							}}
							icon="arrow-top-right"
						/>
					)}
					<div
						className="react-grid-item-content"
						style={{
							...tileStyle,
							backgroundColor:
								tile && !isNaN(tile.room) && tile.color
									? tile.color
									: "#ced9e0",
						}}
					>
						<div
							className="center"
							style={{
								color: contentColor,
								width: "100%",
								maxHeight: tileStyle.maxHeight - 20,
								overflow: "hidden",
							}}
						>
							{!isEmpty(tile) && entities.room[tile.room]
								? entities.room[tile.room].name
								: ""}
							<p>
								{!isEmpty(tile)
									? tile.characters.map((char) => (
											<Tooltip content={entities.character[char].name}>
												{entities.character[char].emoji}
											</Tooltip>
									  ))
									: ""}
							</p>
							<p>
								{!isEmpty(tile)
									? tile.objects.map((obj) => (
											<Tooltip content={entities.object[obj].name}>
												{entities.object[obj].emoji}
											</Tooltip>
									  ))
									: ""}
							</p>
						</div>
					</div>
				</div>
			</div>
		);
	};

	return (
		<Formik
			initialValues={
				inheritedInputs ||
				(!isEmpty(initialInputs) ? initialInputs : undefined) ||
				emptyTileForm
			}
			validate={(values) => {
				let errors = {};
				if (!values.room) {
					errors.room = "Required";
				}
				return errors;
			}}
			isInitialValid={!!inheritedInputs && !!inheritedInputs.room}
			onSubmit={handleSubmit}
		>
			{(props) => {
				const {
					values,
					setFieldValue,
					touched,
					setFieldTouched,
					errors,
					dirty,
					isValid,
					handleSubmit,
					handleReset,
				} = props;
				const setRoomValue = (name, value, fullValue) => {
					setFieldValue(name, value);
					setFieldValue("color", findBiome(fullValue.name, values.color));
				};

				const hasContent = () => {
					return (
						!isNaN(values.room) ||
						!isEmpty(values.characters) ||
						!isEmpty(values.objects)
					);
				};

				return (
					<>
						<Hideable title="Room">
							<SelectFromExistingOrCreateNew
								initialState={selectOrCreateState.CHOOSE}
								SelectFromExisting={BaseSuggest}
								selectFromExistingProps={{
									id: "room-input",
									errors: errors.room,
									touched: touched.room,
									setFieldTouched: setFieldTouched,
									onItemSelect: findOrAddEntity,
									entities: entities,
									handleChange: setRoomValue,
								}}
								handleChange={setFieldValue}
								formValue={values.room}
								name="room"
								type="room"
								Form={RoomForm}
								formProps={{
									initialInputs: emptyRoomForm,
								}}
								handleCreateSubmit={(data) =>
									setRoomValue("room", findOrAddEntity(data, "room"), data)
								}
								handleEditSubmit={editEntity}
								Selected={SelectedTableView}
								selectedProps={{
									columnNames: ["Name", "Description", "Backstory"],
									columnKeys: ["name", "description", "backstory"],
									items: !isNaN(values.room) ? [values.room] : undefined,
									entities,
									type: "room",
								}}
							></SelectFromExistingOrCreateNew>
							{errors.room && touched.room && (
								<div className="form-error">{errors.room}</div>
							)}
							<div style={{ marginTop: "5px" }}>
								<ColorPicker
									colors={TILE_COLORS}
									value={values.color}
									handleChange={setFieldValue}
									advanced
								/>
							</div>
						</Hideable>
						<Hideable
							initialOpen={!isEmpty(values.characters)}
							title="Characters"
						>
							<SelectFromExistingOrCreateNew
								SelectFromExisting={BaseMultiSelect}
								selectFromExistingProps={{
									id: "characters-input",
									errors: errors.characters,
									touched: touched.characters,
									setFieldTouched: setFieldTouched,
									tooltip: "physical_description",
									onItemSelect: (e, type) => {
										e.emoji = findEmoji(e.name);
										return findOrAddEntity(e, type);
									},
									entities: entities,
									handleChange: setFieldValue,
								}}
								handleChange={setFieldValue}
								formValue={values.characters}
								name="characters"
								type="character"
								Form={CharacterForm}
								formProps={{
									initialInputs: emptyCharacterForm,
								}}
								handleCreateSubmit={(data) => {
									data.emoji = findEmoji(data.name);
									setFieldValue(
										"characters",
										values.characters.concat(findOrAddEntity(data, "character"))
									);
								}}
								handleEditSubmit={editEntity}
								Selected={SelectedTableView}
								selectedProps={{
									columnNames: ["Name", "Persona", "Emoji"],
									columnKeys: ["name", "persona", "emoji"],
									items: values.characters,
									entities,
									type: "character",
									editEntity: editEntity,
								}}
							/>
							{errors.characters && touched.characters && (
								<div className="form-error">{errors.characters}</div>
							)}
						</Hideable>
						<Hideable initialOpen={!isEmpty(values.characters)} title="Objects">
							<SelectFromExistingOrCreateNew
								SelectFromExisting={BaseMultiSelect}
								selectFromExistingProps={{
									id: "objects-input",
									errors: errors.objects,
									touched: touched.objects,
									setFieldTouched: setFieldTouched,
									tooltip: "physical_description",
									onItemSelect: (e, type) => {
										e.emoji = findEmoji(e.name);
										return findOrAddEntity(e, type);
									},
									entities: entities,
									handleChange: setFieldValue,
								}}
								handleChange={setFieldValue}
								formValue={values.objects}
								name="objects"
								type="object"
								Form={ObjectForm}
								formProps={{
									initialInputs: emptyObjectForm,
								}}
								handleCreateSubmit={(data) => {
									data.emoji = findEmoji(data.name);
									setFieldValue(
										"objects",
										values.objects.concat(findOrAddEntity(data, "object"))
									);
								}}
								handleEditSubmit={editEntity}
								Selected={SelectedTableView}
								selectedProps={{
									columnNames: ["Name", "Description", "emoji"],
									columnKeys: ["name", "physical_description", "emoji"],
									items: values.objects,
									entities,
									type: "object",
									editEntity: editEntity,
								}}
							/>
							{errors.objects && touched.objects && (
								<div className="form-error">{errors.objects}</div>
							)}
						</Hideable>
						<Hideable title="Preview">
							<TilePreview tile={values} />
						</Hideable>
						<div
							style={{
								display: "flex",
								justifyContent: "flex-end",
								padding: "10px",
							}}
						>
							<Button
								type="reset"
								onClick={handleClear}
								disabled={!hasContent()}
								style={{ marginRight: "15px" }}
							>
								Clear
							</Button>
							<Button
								type="reset"
								onClick={handleReset}
								disabled={!dirty}
								style={{ marginRight: "15px" }}
							>
								Reset
							</Button>
							<Button
								intent={Intent.PRIMARY}
								type="submit"
								onClick={handleSubmit}
								disabled={!isValid}
								style={{ marginLeft: "15px" }}
							>
								Save Changes
							</Button>
						</div>
					</>
				);
			}}
		</Formik>
	);
}

// Container for children that allows children to be hidden
function Hideable({ initialOpen = true, children, title }) {
	const [open, setOpen] = React.useState(initialOpen);

	return (
		<div style={{ margin: "0 0 10px 0" }}>
			<div
				onClick={() => setOpen(!open)}
				className={`hideable-header ${open ? "" : "hidden"}`}
			>
				<Icon
					className={`hideable-arrow ${open ? "" : "hidden"}`}
					icon="chevron-down"
				/>{" "}
				{title}
			</div>
			<AnimateHeight
				duration={500}
				height={open ? "auto" : 0}
				easing={"ease"}
				animateOpacity={true}
			>
				<div className={`hideable-content`}>{children}</div>
			</AnimateHeight>
		</div>
	);
}

// A table view for all selected entities with actions
function SelectedTableView({
	columnNames,
	columnKeys,
	items,
	entities,
	handleEdit,
	handleDuplicate,
	handleDelete,
	type,
	editEntity,
}) {
	function EmojiTD({ item }) {
		const [showPicker, setShowPicker] = React.useState(false);
		return (
			<Popover
				interactionKind={PopoverInteractionKind.CLICK}
				onInteraction={(state) => setShowPicker(state)}
				isOpen={showPicker}
				wrapperTagName="td"
			>
				<div
					// onClick={() => setShowPicker(!showPicker)}
					style={{ height: "100%", width: "100%" }}
				>
					{entities[type][item].emoji || DEFAULT_EMOJI}
				</div>
				<Picker
					onSelect={(event) => {
						const data = cloneDeep(entities[type][item]);
						data.emoji = event.native;
						editEntity(item, data, type);
						setShowPicker(false);
					}}
				/>
			</Popover>
		);
	}
	return (
		<>
			{!isEmpty(items) && (
				<table
					data-testid="table-explore"
					style={{ width: "100%" }}
					className="bp3-html-table bp3-html-table-striped bp3-html-table-condensed bp3-interactive"
				>
					<thead>
						<tr>
							{columnNames.map((col, index) => (
								<th key={index}>{col}</th>
							))}
							<th>Actions</th>
						</tr>
					</thead>
					<tbody>
						{items.map((item, index) => {
							return (
								<React.Fragment key={index}>
									<tr>
										{columnKeys.map((key) => {
											if (key === "emoji") {
												return <EmojiTD item={item} key={key} />;
											}
											return <td key={key}>{entities[type][item][key]}</td>;
										})}
										<td>
											<div style={{ display: "flex", flexDirection: "row" }}>
												<Button
													onClick={() => handleEdit(item, entities[type][item])}
													icon="edit"
													minimal
												/>
												<Button
													onClick={() => handleDuplicate(entities[type][item])}
													icon="duplicate"
													minimal
												/>
												<Button
													onClick={() => handleDelete(index)}
													icon="trash"
													minimal
												/>
											</div>
										</td>
									</tr>
								</React.Fragment>
							);
						})}
					</tbody>
				</table>
			)}
		</>
	);
}

const selectOrCreateState = {
	BASE: 0,
	CHOOSE: 1,
	SELECT_FROM_EXISTING: 2,
	CREATE_NEW: 3,
	EDIT: 4,
	DUPLICATE: 5,
};

// Input type component that includes the selected table,
// a component for selecting from existing,
// and a form for creating new/editing/duplicating
function SelectFromExistingOrCreateNew({
	initialState = selectOrCreateState.BASE,
	handleChange,
	name,
	type,
	formValue,
	SelectFromExisting,
	selectFromExistingProps,
	Form,
	formProps,
	handleCreateSubmit,
	handleEditSubmit,
	Selected,
	selectedProps,
}) {
	const [state, setState] = React.useState(initialState);
	const [editing, setEditing] = React.useState(undefined);
	const [duplicating, setDuplicating] = React.useState(undefined);

	const handleEditClick = (id, data) => {
		setEditing({ id, data });
		setState(selectOrCreateState.EDIT);
	};

	const handleDuplicate = (data) => {
		setDuplicating(data);
		setState(selectOrCreateState.DUPLICATE);
	};

	const handleDelete = (index) => {
		if (Array.isArray(formValue)) {
			formValue.splice(index, 1);
			handleChange(name, formValue);
		} else {
			handleChange(name, undefined);
		}
	};

	return (
		<>
			<Selected
				{...selectedProps}
				handleEdit={handleEditClick}
				handleDuplicate={handleDuplicate}
				handleDelete={handleDelete}
			/>
			{state === selectOrCreateState.CHOOSE ? (
				// choose between creating new or selecting from existing
				<div
					style={{
						display: "flex",
						justifyContent: "center",
						flexDirection: "row",
						alignItems: "center",
						padding: "5px",
					}}
				>
					<Button
						onClick={() => setState(selectOrCreateState.SELECT_FROM_EXISTING)}
						style={{ margin: "5px" }}
					>
						Select from existing
					</Button>
					<span style={{ margin: "5px" }}> OR </span>
					<Button
						onClick={() => setState(selectOrCreateState.CREATE_NEW)}
						style={{ margin: "5px" }}
					>
						Create New
					</Button>
				</div>
			) : state === selectOrCreateState.SELECT_FROM_EXISTING ? (
				// selecting from existing
				<div>
					<Button
						onClick={() => setState(initialState)}
						icon="chevron-left"
						minimal
					/>
					<SelectFromExisting
						{...selectFromExistingProps}
						name={name}
						type={type}
						formValue={formValue}
					/>
				</div>
			) : state === selectOrCreateState.CREATE_NEW ? (
				// creating new
				<div>
					<Button
						onClick={() => setState(initialState)}
						icon="chevron-left"
						minimal
					/>
					<Form
						{...formProps}
						type={type}
						handleSubmit={(value) => {
							setState(initialState);
							handleCreateSubmit(value);
						}}
					/>
				</div>
			) : state === selectOrCreateState.EDIT ? (
				// editing
				<div>
					<Button
						onClick={() => setState(initialState)}
						icon="chevron-left"
						minimal
					/>
					<Form
						{...formProps}
						type={type}
						initialInputs={editing.data}
						handleSubmit={(value) => {
							setState(initialState);
							handleEditSubmit(editing.id, value, type);
							setEditing(undefined);
						}}
					/>
				</div>
			) : state === selectOrCreateState.DUPLICATE ? (
				// duplicating
				<div>
					<Button
						onClick={() => setState(initialState)}
						icon="chevron-left"
						minimal
					/>
					<Form
						{...formProps}
						type={type}
						initialInputs={duplicating}
						handleSubmit={(value) => {
							setState(initialState);
							handleCreateSubmit(value);
							setDuplicating(undefined);
						}}
					/>
				</div>
			) : (
				<Button onClick={() => setState(selectOrCreateState.CHOOSE)} icon="add">
					Add
				</Button>
			)}
		</>
	);
}

export default AdvancedTileForm;
