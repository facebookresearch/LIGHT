/* REACT */
import React, {useState} from "react";
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
  isLoading
}) => {
  const [isClicked, setIsClicked] = useState(false)
  const generateFunction = async ()=>{
    try {
      setIsClicked(true)
      await clickFunction()
      setIsClicked(false)
    }
    catch (err){
      setIsClicked(false)
      throw err
      console.log(err)
    }
  }
  return (
    <Button className="generatebutton-container" onClick={generateFunction} variant="primary" disabled={isLoading}>
    {
        (isLoading && isClicked)
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
        label !== undefined ? label  : "Generate"
    }
    </Button>
  );
};

export default GenerateButton;
