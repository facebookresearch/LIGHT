
import React, { Component } from 'react';
import Button from 'react-bootstrap/Button';

class Card extends Component {
  constructor() {
    super();

    this.state = {
      showMenu: false,
    };

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
                <Button variant="outline-primary"> Menu item 1 </Button>
                <Button variant="outline-primary"> Menu item 2 </Button>
                <Button variant="outline-primary"> Menu item 3 </Button>
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

export { Card };
