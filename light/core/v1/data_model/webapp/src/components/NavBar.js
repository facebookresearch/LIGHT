import React from "react";
import {
  Navbar,
  Alignment,
  Button,
  Position,
  Popover,
  Menu,
  MenuItem
} from "@blueprintjs/core";
import { Link } from "react-router-dom";

import WorldFileUpload from "./WorldFileUpload";

function NavBar({ children }) {
  const [worldBuildPopover, setWorldBuildPopover] = React.useState(false);
  return (
    <React.Fragment>
      <Navbar>
        <Navbar.Group align={Alignment.LEFT}>
          <Navbar.Heading>LIGHT Data Model</Navbar.Heading>
          <Navbar.Divider />
          <Link data-testid="link-explore" className="btn-link" to="/explore">
            <Button className="bp3-minimal" icon="path-search" text="Explore" />
          </Link>
          <Link data-testid="link-create" className="btn-link" to="/create">
            <Button className="bp3-minimal" icon="cube" text="Create" />
          </Link>
          <Link data-testid="link-review" className="btn-link" to="/review">
            <Button className="bp3-minimal" icon="form" text="Review Edits" />
          </Link>
          <Popover
            position={Position.BOTTOM_LEFT}
            minimal
            isOpen={worldBuildPopover}
          >
            <Button
              onClick={() => setWorldBuildPopover(!worldBuildPopover)}
              className="bp3-minimal"
              icon="map-create"
              text="Build World"
            />
            <Menu>
              <MenuItem
                icon="new-object"
                text={
                  <Link
                    onClick={() => setWorldBuildPopover(false)}
                    style={{ color: "inherit" }}
                    data-testid="link-world-builder"
                    className="btn-link"
                    to="/world_builder"
                  >
                    Create New
                  </Link>
                }
                shouldDismissPopover={true}
                tagName="div"
              />
              <WorldFileUpload setPopover={setWorldBuildPopover} />
            </Menu>
          </Popover>
        </Navbar.Group>
      </Navbar>
      {children}
    </React.Fragment>
  );
}

export default NavBar;
