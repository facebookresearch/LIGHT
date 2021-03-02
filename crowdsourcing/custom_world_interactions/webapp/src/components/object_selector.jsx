
import React, { Component } from 'react';
import Button from 'react-bootstrap/Button';

class ObjectSelector extends Component {
  constructor(props) {
    super();

    this.state = {
      showMenu: false,
    };

    console.log('props', props);
    this.objectList = props.objectList;
    console.log('Object List: ', this.objectList);
    this.showMenu = this.showMenu.bind(this);
    this.closeMenu = this.closeMenu.bind(this);
  }

  showMenu(event) {
    event.preventDefault();

    this.setState({ showMenu: true }, () => {
      document.addEventListener('click', this.closeMenu);
    });
  }

  closeMenu(event) {

    if (!this.dropdownMenu.contains(event.target)) {

      this.setState({ showMenu: false }, () => {
        document.removeEventListener('click', this.closeMenu);
      });

    }
  }

  render() {
    const objects = []
    for (const [index, object] of this.objectList.entries()) {
      objects.push(<Button key={index} variant="outline-primary">{object}</Button>);
    }

    return (
      <div>
        <Button variant="outline-primary" onClick={this.showMenu}>
          Show menu
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
