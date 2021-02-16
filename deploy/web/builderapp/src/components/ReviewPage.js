import React from "react";
import {
	Button,
	Checkbox,
	Classes,
	Dialog,
	Intent,
	Radio,
	RadioGroup,
	Spinner,
} from "@blueprintjs/core";
import DiffMatchPatch from "diff-match-patch";
import AnimateHeight from "react-animate-height";
import { startCase, fill } from "lodash";

import CONFIG from "../config";
import { useAPI, post } from "../utils";
import AppToaster from "./AppToaster";

function ReviewPage() {
	const [selectedStatus, setSelectedStatus] = React.useState("under review");

	const { loading, result, reload } = useAPI(
		CONFIG,
		`/edits?expand=true&status=${selectedStatus}`
	);

	return (
		<div>
			<h2 data-testid="header" className="bp3-heading">
				Review
			</h2>
			<div className="bp3-text-large">
				Review pending, accepted, and rejected edits to the LIGHT database.
			</div>
			<br />
			<div style={{ display: "flex", marginBottom: "30px" }}>
				<span style={{ margin: "0px 20px 0px 40px" }}>Searching category:</span>
				<RadioGroup
					inline
					large
					onChange={(e) => setSelectedStatus(e.target.value)}
					selectedValue={selectedStatus}
				>
					<Radio
						data-testid="radio-under-review"
						label="Under Review"
						value="under review"
					/>
					<Radio
						data-testid="radio-accepted"
						label="Accepted"
						value="accepted"
					/>
					<Radio
						data-testid="radio-rejected"
						label="Rejected"
						value="rejected"
					/>
				</RadioGroup>
			</div>
			{loading ? (
				<Spinner intent={Intent.PRIMARY} />
			) : (
				<EditsList edits={result} status={selectedStatus} reload={reload} />
			)}
		</div>
	);
}

function EditsList({ edits, status, reload }) {
	const [state, setState] = React.useState({
		expanded: -1,
		animating: 0,
		nextState: -1,
	});
	const [selected, setSelected] = React.useState({ rows: [], all: 0 });
	const [submitAction, setSubmitAction] = React.useState(undefined);
	const [showDialog, setShowDialog] = React.useState(false);
	const [pendingSubmission, setPendingSubmission] = React.useState([]);

	if (edits && edits.length > 0 && selected.rows.length === 0) {
		setSelected({ ...selected, rows: fill(Array(edits.length), false) });
	}

	function handleTdClick(index) {
		if (status === "under review") {
			if (state.expanded === -1) {
				setState({ expanded: index, animating: 1, nextState: -1 });
			} else if (state.expanded === index) {
				setState({ expanded: index, animating: 3, nextState: -1 });
			} else {
				setState({ ...state, animating: 3, nextState: index });
			}
		}
	}

	function handleCheckbox(index) {
		const newSelection = [...selected.rows];
		newSelection[index] = selected.rows[index] ? false : true;
		let all = selected.all;
		if (newSelection.every((r) => r === true)) {
			all = 1;
		} else if (newSelection.every((r) => r === false)) {
			all = 0;
		} else {
			all = -1;
		}
		setSelected({ rows: newSelection, all });
	}

	function handleSelectAll() {
		const all = selected.all ? 0 : 1;
		const newRows = fill(Array(edits.length), !!all);
		setSelected({ rows: newRows, all });
	}

	async function handleSubmitSelected() {
		const reqs = pendingSubmission.map((index) =>
			post(`builder/edits/${edits[index].edit_id}/${submitAction}`)
		);
		await Promise.all(reqs).then(() => {
			reload();
		});
		AppToaster.show({ intent: Intent.SUCCESS, message: "Review submitted" });
	}

	const showSubmission = (action) => {
		const checked = [];
		for (let i = 0; i < selected.rows.length; i++) {
			if (selected.rows[i]) {
				checked.push(i);
			}
		}
		setPendingSubmission(checked);
		setSubmitAction(action);
		setShowDialog(true);
	};

	if (edits === undefined || edits.length === 0) {
		return <span>No edits found.</span>;
	} else {
		return (
			<>
				<Dialog
					icon="info-sign"
					onClose={() => setShowDialog(false)}
					title={`Confirm edits to be ${
						submitAction === "reject" ? "rejected" : "accepted"
					}`}
					isOpen={showDialog}
					usePortal={false}
				>
					<div className={Classes.DIALOG_BODY}>
						<table className="bp3-html-table bp3-html-table-condensed bp3-interactive">
							<thead>
								<tr>
									<th>Edit ID</th>
									<th>Entity ID</th>
									<th>Edited Field</th>
								</tr>
							</thead>
							<tbody>
								{pendingSubmission.map((edit, index) => {
									return (
										<tr key={index}>
											<td>{edits[edit].edit_id}</td>
											<td>{edits[edit].id}</td>
											<td>{edits[edit].field}</td>
										</tr>
									);
								})}
							</tbody>
						</table>
					</div>
					<div className={Classes.DIALOG_FOOTER}>
						<div className={Classes.DIALOG_FOOTER_ACTIONS}>
							<Button onClick={() => setShowDialog(false)}>Close</Button>
							<Button intent={Intent.PRIMARY} onClick={handleSubmitSelected}>
								Confirm Edits
							</Button>
						</div>
					</div>
				</Dialog>
				<table
					data-testid="table-review"
					style={{ width: "100%" }}
					className="bp3-html-table bp3-html-table-condensed bp3-interactive"
				>
					<thead>
						<tr>
							{status === "under review" && (
								<th style={{ textAlign: "center" }}>
									<Checkbox
										checked={selected.all}
										indeterminate={selected.all === -1}
										onClick={handleSelectAll}
									/>
								</th>
							)}
							<th>Edit ID</th>
							<th>Entity ID</th>
							<th>Edited Field</th>
							<th>Edit</th>
						</tr>
					</thead>
					<tbody>
						{edits.map((edit, index) => (
							<React.Fragment key={edit.edit_id}>
								<tr
									data-testid="tr-review"
									style={{
										background:
											index % 2 === 0 ? "rgba(191, 204, 214, 0.15)" : undefined,
									}}
								>
									{status === "under review" && (
										<td style={{ textAlign: "center" }}>
											<Checkbox
												checked={selected.rows[index]}
												onClick={() => handleCheckbox(index)}
											/>
										</td>
									)}
									<td onClick={() => handleTdClick(index)}>{edit.edit_id}</td>
									<td onClick={() => handleTdClick(index)}>
										<strong>{edit.id}</strong>
									</td>
									<td onClick={() => handleTdClick(index)}>{edit.field}</td>
									<td onClick={() => handleTdClick(index)}>
										{diff(edit.unedited_value, edit.edited_value)}
									</td>
								</tr>
								<tr
									style={{
										background:
											index % 2 === 0 ? "rgba(191, 204, 214, 0.15)" : undefined,
									}}
								>
									<td
										colSpan={5}
										style={{
											display: state.expanded === index ? undefined : "none",
											padding: 0,
											cursor: "unset",
										}}
									>
										<AnimateHeight
											duration={500}
											height={
												state.expanded === index &&
												(state.animating === 2 || state.animating === 0)
													? "auto"
													: 0
											}
											easing={"ease"}
											onAnimationEnd={() =>
												setState({
													nextState: -1,
													expanded:
														state.animating === 2 ? index : state.nextState,
													animating:
														state.animating === 3 && state.nextState !== -1
															? 1
															: 0,
												})
											}
											animateOpacity={true}
										>
											{state.expanded === index && (
												<ExpandedTab
													edit={edit}
													state={state}
													setState={setState}
													reload={reload}
												/>
											)}
										</AnimateHeight>
									</td>
								</tr>
							</React.Fragment>
						))}
					</tbody>
				</table>
				{status === "under review" && (
					<div
						style={{
							display: "flex",
							margin: "10px",
							justifyContent: "flex-end",
						}}
					>
						<Button
							intent={Intent.DANGER}
							type="submit"
							onClick={() => showSubmission("reject")}
							style={{ marginLeft: "15px" }}
							disabled={!selected.all}
						>
							Reject
						</Button>
						<Button
							intent={Intent.SUCCESS}
							type="submit"
							onClick={() => showSubmission("accept/accepted")}
							style={{ marginLeft: "15px" }}
							disabled={!selected.all}
						>
							Accept
						</Button>
					</div>
				)}
			</>
		);
	}
}

function ExpandedTab({ edit, state, setState, reload }) {
	const { loading, result } = useAPI(CONFIG, `/entities/${edit.id}`);
	React.useEffect(() => {
		if (result && state.animating === 1) {
			setState({ ...state, animating: 2 });
		}
	}, [loading, setState, state, result]);
	return (
		<>
			{loading ? (
				<></>
			) : (
				<Card edit={edit} entity={result.entity} reload={reload} />
			)}
		</>
	);
}

function Card({ edit, entity, reload }) {
	delete entity.id;
	return (
		<>
			<div
				data-testid="dropdown"
				style={{
					display: "flex",
					flexDirection: "row",
					padding: "20px 20px 0 20px",
					alignItems: "center",
				}}
			>
				<div style={{ flexGrow: 1 }}>
					<div
						style={{
							display: "flex",
							flexDirection: "column",
							width: "50%",
							maxWidth: "30vw",
							margin: "auto",
						}}
					>
						{Object.keys(entity).map((key, index) => (
							<p
								key={index}
								style={{ color: key === edit.field ? "#DB3737" : undefined }}
							>
								<strong>{startCase(key)}</strong>: {entity[key]}
							</p>
						))}
					</div>
				</div>
				<div style={{ height: "100%", fontSize: "20px", color: "#394B59" }}>
					➔
				</div>
				<div style={{ flexGrow: 1 }}>
					<div
						style={{
							display: "flex",
							flexDirection: "column",
							width: "50%",
							maxWidth: "30vw",
							margin: "auto",
						}}
					>
						{Object.keys(entity).map((key, index) => (
							<p
								key={index}
								style={{ color: key === edit.field ? "#0F9960" : undefined }}
							>
								<strong>{startCase(key)}</strong>:{" "}
								{key === edit.field ? edit.edited_value : entity[key]}
							</p>
						))}
					</div>
				</div>
			</div>
			<div
				style={{
					display: "flex",
					padding: "0 20px 20px 20px",
					justifyContent: "flex-end",
				}}
			>
				<Button
					intent={Intent.DANGER}
					type="submit"
					onClick={() =>
						post(`builder/edits/${edit.edit_id}/reject`).then(() => reload())
					}
					style={{ marginLeft: "15px" }}
				>
					Reject Edit
				</Button>
				<Button
					intent={Intent.SUCCESS}
					type="submit"
					onClick={() =>
						post(`builder/edits/${edit.edit_id}/accept/accepted`).then(() =>
							reload()
						)
					}
					style={{ marginLeft: "15px" }}
				>
					Accept Edit
				</Button>
			</div>
		</>
	);
}

function diff(orig, edit) {
	let diff;
	if (isNaN(orig) || isNaN(edit)) {
		const differ = new DiffMatchPatch();
		diff = differ.diff_main(orig, edit);
		differ.diff_cleanupSemantic(diff);
	} else {
		orig = 0 + orig;
		edit = 0 + edit;
		diff = [
			[-1, +orig],
			[1, +edit],
		];
	}
	return (
		<>
			{diff.map((d, index) => {
				switch (d[0]) {
					case -1:
						return (
							<strike key={index} style={{ color: "#FF7373" }}>
								{" "}
								{d[1]}{" "}
							</strike>
						);
					case 0:
						return <strong key={index}>{d[1]}</strong>;
					case 1:
						return (
							<strong key={index} style={{ color: "#0F9960" }}>
								{d[1]}
							</strong>
						);
					default:
						return <></>;
				}
			})}
		</>
	);
}

export default ReviewPage;
