import React from "react";

export default function Logo() {
	const builder_url =
		window.location.protocol + "//" + window.location.host + "/builder/";
	return (
		<div className="header">
			<img alt="logo" src="/scribe.png" />
			<div>
				<h1>LIGHT</h1>
				<span>Learning in Interactive Games with Humans and Text</span>
				<p>
					<a href={builder_url} rel="noopener noreferrer" target="_blank">
						Go To World Builder
					</a>
				</p>
			</div>
		</div>
	);
}
