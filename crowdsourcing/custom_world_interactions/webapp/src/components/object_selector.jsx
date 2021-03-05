
import React, { Component } from 'react';
import Button from 'react-bootstrap/Button';

class ObjectSelector extends Component {
  constructor(props) {
    super();

    this.state = {
      showMenu: false,
    };

    this.objectList = props.objectList;
    this.selectedTargetObject = "";
  }

  getSelectedTargetObject() {
    return this.selectedTargetObject;
  }

  setSelectedTargetObject(selectedTargetObject) {
    this.selectedTargetObject = selectedTargetObject;
  }

  showMenu() {
    this.state.showMenu = true;
  }

  hideMenu() {
    this.state.showMenu = false;
  }

  render() {
    const objects = []
    for (const [index, object] of this.objectList.entries()) {
      objects.push(
        <Button
          key={index}
          variant="outline-primary"
          onClick={ (key) => {this.setSelectedTargetObject(this.objectList[key])} }>
            {object}
        </Button>
      );
    }
    console.log(this.getSelectedTargetObject());

    return (
      <div>
        <p>{this.selectedTargetObject}</p>
        <Button variant="outline-primary" onClick={ this.state.showMenu ? this.hideMenu : this.showMenu }>
          { this.state.showMenu ? "Hide menu" : "Show menu" }
        </Button>
        {
          this.state.showMenu
            ? (
              <div
                className="menu"
                ref={(element) => {
                  this.dropdownMenu = element;
                }}
              >
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
}

export { ObjectSelector };
