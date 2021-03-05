
import React, { Component } from 'react';
import Button from 'react-bootstrap/Button';

function ObjectSelector({ objectList, currentSelectedObject, onChangeCurrentSelectedObject }) {
  const [showMenu, setShowMenu] = React.useState(false);

  const objects = []
  for (const [index, object] of objectList.entries()) {
    objects.push(
      <Button
        key={index}
        variant="outline-primary"
        onClick={
          () => { onChangeCurrentSelectedObject(object); }
        }>
          {object}
      </Button>
    )
  }

  return (
    <div>
      <Button variant="outline-primary" onClick={ () => { setShowMenu(!showMenu) } }>
        { showMenu ? "Hide menu" : "Show menu" }
      </Button>
      {
        showMenu
          ? (
            <div className="menu">
              {objects}
            </div>
          )
          : (
            null
          )
      }
    </div>
  );
}

export { ObjectSelector };
