/* REACT */
import React, {forwardRef, useState} from "react";
/* REACT ROUTER */
import { HashRouter, Route, Redirect } from "react-router-dom";

/* BOOTSTRAP COMPONENTS */
import Dropdown from 'react-bootstrap/Dropdown'
import FormControl from 'react-bootstrap/FormControl'
/* CUSTOM COMPONENTS */


const SearchBar = ({
    data,
    filterFunction
})=>{

  const CustomMenu = forwardRef(
    ({ children, style, className, 'aria-labelledby': labeledBy }, ref) => {
      const [value, setValue] = useState('');

      return (
        <div
          ref={ref}
          style={style}
          className={className}
          aria-labelledby={labeledBy}
        >
          <FormControl
            autoFocus
            className="mx-3 my-2 w-auto"
            placeholder="Type to filter..."
            onChange={(e) => setValue(e.target.value)}
            value={value}
          />
          <ul className="list-unstyled">
            {React.Children.toArray(children).filter(
              (child) =>
                !value || child.props.children.toLowerCase().startsWith(value),
            )}
          </ul>
        </div>
      );
    },
  );

  return(
    <>
      <CustomMenu>
        {/* <Dropdown.Item eventKey="1"></Dropdown.Item> */}

      </CustomMenu>
    </>
  );
}

export default SearchBar
