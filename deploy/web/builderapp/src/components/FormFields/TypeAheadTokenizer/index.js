/* REACT */
import React, {useState, useEffect} from 'react';

import { Typeahead } from 'react-bootstrap-typeahead';

/* BOOTSTRAP COMPONENTS */
//LAYOUT
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';


const TypeAheadTokenizerForm = ({
    formLabel
})=>{

    return(
        <div>
            <h5>{formLabel}</h5>
            <Typeahead
                multiple
                labelKey={option => `${option.firstName} ${option.lastName}`}
                options={[
                    {firstName: 'Art', lastName: 'Blakey'},
                    {firstName: 'Jimmy', lastName: 'Cobb'},
                    {firstName: 'Elvin', lastName: 'Jones'},
                    {firstName: 'Max', lastName: 'Roach'},
                    {firstName: 'Tony', lastName: 'Williams'},
                  ]}
            />
        </div>
    )
}

export default TypeAheadTokenizerForm;