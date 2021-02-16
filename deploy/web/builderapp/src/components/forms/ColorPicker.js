import React from "react";

function ColorPicker({ colors, value, handleChange, advanced }) {
	return (
		<div
			style={{ display: "flex", flexDirection: "row", alignItems: "center" }}
		>
			{colors.map((color, index) => {
				return (
					<div
						key={index}
						style={{
							display: "inline-block",
							maxWidth: "20px",
							width: "20px",
							maxHeight: "20px",
							height: "20px",
							borderRadius: "5px",
							background: color,
							borderColor: "#5C7080",
							borderStyle: value === color ? "solid" : "",
							borderWidth: "2px",
							boxShadow: value === color ? `0px 0px 8px ${value}` : "",
							margin: "2px",
							cursor: "pointer",
						}}
						onClick={() => handleChange("color", color)}
					/>
				);
			})}
			{advanced && (
				<input
					style={{
						maxHeight: "20px",
						maxWidth: "20px",
						height: "20px",
						width: "20px",
						borderRadius: "5px",
						padding: "0px 0px 0px 0px",
					}}
					type="color"
					value={value}
					onChange={(event) => handleChange("color", event.target.value)}
				/>
			)}
		</div>
	);
}

export default ColorPicker;
