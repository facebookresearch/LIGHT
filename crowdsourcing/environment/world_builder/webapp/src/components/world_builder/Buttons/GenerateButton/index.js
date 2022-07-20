/* REACT */
import React from "react";
/* STYLES */
import "./styles.css";
/* BOOTSTRAP COMPONENTS */
//BUTTON
import Button from 'react-bootstrap/Button';
import Spinner from 'react-bootstrap/Spinner';


//TextButton -
const GenerateButton = ({
  clickFunction,
  label,
  isloading
}) => {
  return (
    <Button className="generatebutton-container" onClick={clickFunction} variant="primary" disabled={isLoading}>
    {
        isloading
        ?
        <>
          <Spinner
              as="span"
              animation="grow"
              size="sm"
              role="status"
              aria-hidden="true"
          />
          GENERATING...
        </>
        :
        generateName !== undefined ? label  : "Generate"
    }
    </Button>
  );
};

export default GenerateButton;
