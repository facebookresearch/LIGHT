import React from "react";
import GridLayout from "react-grid-layout";
import { cloneDeep, isEmpty, isEqual } from "lodash";
import { Button, Drawer, Classes } from "@blueprintjs/core";

import Tile from "./Tile";
import { MAX_HEIGHT, MAX_WIDTH } from "./utils";
import AdvancedTileForm from "../forms/AdvancedTileForm";

const SIZE = 150;
const MARGIN = 24;

/**
 * Helper function to get a neighbor for the given tile. Right now only returns one
 * rather than trying to suggest based on all of them.
 */
function get_neighbor(j, i, state) {
  let otherTile = state.getTileAt(j - 1, i, state.currFloor);
  if (otherTile && !isNaN(otherTile.room)) {
    return otherTile.room;
  }
  otherTile = state.getTileAt(j + 1, i, state.currFloor);
  if (otherTile && !isNaN(otherTile.room)) {
    return otherTile.room;
  }
  otherTile = state.getTileAt(j, i - 1, state.currFloor);
  if (otherTile && !isNaN(otherTile.room)) {
    return otherTile.room;
  }
  otherTile = state.getTileAt(j, i + 1, state.currFloor);
  if (otherTile && !isNaN(otherTile.room)) {
    return otherTile.room;
  }

	return undefined;
}

/**
 * Component for the interactive grid.
 * Using react-grid-layout for the draggable interface with some custom drag behavior to maintain
 * grid dimensions and update map state.
 */
function Grid({ state, initialShowAdvanced }) {
	const [layout, setLayout] = React.useState(null);
	const [selected, setSelected] = React.useState(null);
	const [showAdvanced, setShowAdvanced] = React.useState(false);
	const [dragging, setDragging] = React.useState(false);

	React.useEffect(() => {
		setShowAdvanced(initialShowAdvanced);
	}, [initialShowAdvanced]);

	const resetShowAdvanced = () => {
		setShowAdvanced(initialShowAdvanced);
	};

	// store the initial layout of the grid
	const onDragStart = (layout) => {
		setLayout(cloneDeep(layout));
	};

	// prevent column growing by swapping position with colliding tile
	const onDragEvent = (newState, initial, next) => {
		if (!isEqual(initial, next)) {
			setDragging(true);
			setSelected(null);
		}
		for (let i = 0; i < layout.length; i++) {
			if (layout[i].i === next.i) {
				continue;
			}
			if (
				layout[i].x === next.x &&
				layout[i].y === next.y &&
				layout[i].i !== next.i
			) {
				newState[i].x = initial.x;
				newState[i].y = initial.y;
			} else {
				newState[i].x = layout[i].x;
				newState[i].y = layout[i].y;
			}
		}

		return true;
	};

	// sets up for the layout to be updated in the superstate
	const onDragStop = (newState, initial, next) => {
		onDragEvent(newState, initial, next);
		setLayout([initial.x, initial.y, next.x, next.y]);
	};

	// update superstate (updating in onDragStop causes tiles to vanish)
	const handleLayoutChange = () => {
		if (layout) {
			const [x1, y1, x2, y2] = layout;
			if (!(x1 === x2 && y1 === y2)) {
				// allows the animation to finish
				setTimeout(() => state.swapTiles(x1, y1, x2, y2), 300);
			}
			setLayout(null);
		}
	};

	// Generate children for GridLayout component
	const generateTiles = () => {
		const tiles = [];
		for (let i = 0; i < state.dimensions.height; i++) {
			for (let j = 0; j < state.dimensions.width; j++) {
				// tile will contain all form data and stair data, or be empty
				const tile = state.getTileAt(j, i, state.currFloor);
				// tile data is used in the key to force GridLayout to rerender the div component
				// and update isDraggable under data-grid
				const key = `${state.currFloor} ${j} ${i} ${
					tile && tile && tile.room ? tile.room.id : ""
				}`;
				tiles.push(
					<div
						key={key}
						data-grid={{
							x: j,
							y: i,
							w: 1,
							h: 1,
							draggableHandle: ".react-grid-item-handle",
							draggableCancel: ".react-grid-item",
							isDraggable: !isEmpty(tile),
						}}
						onClick={() => {
							if (
								!dragging &&
								(!selected ||
									(selected && (selected.x !== j || selected.y !== i)))
							) {
								setSelected({ x: j, y: i });
							} else {
								setDragging(false);
							}
						}}
					>
						<Tile
							x={j}
							y={i}
							tile={tile}
							selected={selected}
							setSelected={setSelected}
							showAdvanced={showAdvanced}
							setShowAdvanced={setShowAdvanced}
							setTile={state.setTile}
							clearTile={state.clearTile}
							getTileAt={state.getTileAt}
							currFloor={state.currFloor}
							tileStyle={{
								width: SIZE,
								height: SIZE,
								maxWidth: SIZE,
								maxHeight: SIZE,
							}}
							state={state}
							neighbor={get_neighbor(j, i, state)}
						/>
					</div>
				);
			}
		}
		return tiles;
	};

	// Generate all walls for the floor
	const generateWalls = () => {
		const walls = [];
		for (let i = 0; i < state.dimensions.height; i++) {
			for (let j = 0; j < state.dimensions.width; j++) {
				// vertical walls
				if (j > 0) {
					const key = `${j - 1} ${i}|${j} ${i}`;
					walls.push(
						<div
							key={key}
							onClick={() => state.toggleWall(key)}
							className={`wall ${
								state.map[state.currFloor].walls[key] ? "active" : ""
							}`}
							style={{
								top: MARGIN + (MARGIN + SIZE) * i,
								left: (MARGIN + SIZE) * j + (MARGIN - 10) / 2,
								height: SIZE,
							}}
						/>
					);
				}
				// horizontal walls
				if (i > 0) {
					const key = `${j} ${i - 1}|${j} ${i}`;
					walls.push(
						<div
							key={key}
							onClick={() => state.toggleWall(key)}
							className={`wall ${
								state.map[state.currFloor].walls[key] ? "active" : ""
							}`}
							style={{
								left: MARGIN + (MARGIN + SIZE) * j,
								top: (MARGIN + SIZE) * i + (MARGIN - 10) / 2,
								width: SIZE,
							}}
						/>
					);
				}
			}
		}
		return walls;
	};

	return (
		<>
			<div
				style={{
					width:
						state.dimensions.width * SIZE +
						(state.dimensions.width + 1) * MARGIN +
						60,
					margin: "0 auto 75px auto",
					textAlign: "center",
				}}
			>
				<Button
					className="bp3-button"
					disabled={state.dimensions.height >= 10}
					style={{
						width:
							state.dimensions.width * SIZE +
							(state.dimensions.width + 1) * MARGIN -
							20,
						margin: "auto",
					}}
					onClick={state.addRowTop}
					icon="add"
				/>
				<div style={{ display: "flex" }}>
					<Button
						className="bp3-button"
						disabled={state.dimensions.width >= 10}
						style={{
							height:
								state.dimensions.height * SIZE +
								(state.dimensions.height + 1) * MARGIN -
								20,
							margin: "10px 0",
						}}
						onClick={state.addColFront}
						icon="add"
					/>
					<div
						className="map-container"
						style={{
							width:
								state.dimensions.width * SIZE +
								(state.dimensions.width + 1) * MARGIN,
							height:
								state.dimensions.height * SIZE +
								(state.dimensions.height + 1) * MARGIN,
						}}
					>
						<div className="walls">{generateWalls()}</div>
						<GridLayout
							cols={state.dimensions.width}
							rowHeight={SIZE}
							width={
								state.dimensions.width * SIZE +
								(state.dimensions.width + 1) * MARGIN
							}
							onDragStart={onDragStart}
							onDrag={onDragEvent}
							onDragStop={onDragStop}
							margin={[MARGIN, MARGIN]}
							onLayoutChange={handleLayoutChange}
							isResizable={false}
							maxRows={state.dimensions.height}
							style={{
								width:
									state.dimensions.width * SIZE +
									(state.dimensions.width + 1) * MARGIN,
							}}
						>
							{generateTiles()}
						</GridLayout>
					</div>
					<Button
						className="bp3-button"
						disabled={state.dimensions.width >= MAX_WIDTH}
						style={{
							height:
								state.dimensions.height * SIZE +
								(state.dimensions.height + 1) * MARGIN -
								20,
							margin: "10px 0",
						}}
						onClick={state.addColEnd}
						icon="add"
					/>
				</div>
				<Button
					className="bp3-button"
					disabled={state.dimensions.height >= MAX_HEIGHT}
					style={{
						width:
							state.dimensions.width * SIZE +
							(state.dimensions.width + 1) * MARGIN -
							20,
						margin: "auto",
					}}
					onClick={state.addRowBot}
					icon="add"
				/>
			</div>
			<AdvancedEditor
				showAdvanced={showAdvanced}
				selected={selected}
				setSelected={setSelected}
				resetShowAdvanced={resetShowAdvanced}
				state={state}
			/>
		</>
	);
}

function AdvancedEditor({
	selected,
	setSelected,
	resetShowAdvanced,
	showAdvanced,
	state,
}) {
	const handleSubmit = (data) => {
		state.setTile(selected.x, selected.y, {
			...state.getTileAt(selected.x, selected.y),
			...data,
		});
		setSelected(null);
		resetShowAdvanced();
	};

	const handleClear = () => {
		state.clearTile(selected.x, selected.y);
		setSelected(null);
		resetShowAdvanced();
	};

	return (
		<Drawer
			icon="build"
			title="Build Tile"
			isOpen={showAdvanced && selected}
			onClose={() => {
				setSelected(null);
				resetShowAdvanced();
			}}
		>
			<div className={Classes.DRAWER_BODY}>
				<div className={Classes.DIALOG_BODY}>
					{selected && (
						<AdvancedTileForm
							x={selected.x}
							y={selected.y}
							currFloor={state.currFloor}
							getTileAt={state.getTileAt}
							initialInputs={state.getTileAt(selected.x, selected.y)}
							inheritedInputs={selected.data}
							handleSubmit={handleSubmit}
							handleClear={handleClear}
							tileStyle={{
								width: SIZE,
								height: SIZE,
								maxWidth: SIZE,
								maxHeight: SIZE,
							}}
							entities={state.entities}
							findOrAddEntity={state.findOrAddEntity}
							editEntity={state.editEntity}
						/>
					)}
				</div>
			</div>
		</Drawer>
	);
}

export default Grid;
