import React from "react";
import Form from 'react-bootstrap/Form';

function TimesComponent ({ setTimesRemaining }) {
    return (
        <div>
            <div className="title is-4">
                <p>How many times can this event occur?</p>
            </div>
            <hr/>
            <p>Please select how many times this interaction could happen. If it can happen <b>infinite times</b>, just type <b>"inf".</b></p>
            <Form inline>
                <Form.Control
                    className="mb-2 mr-sm-2"
                    id="inlineFormInputName2"
                    placeholder="Times remaining for this interaction"
                    onChange={(e)=>{setTimesRemaining(e.target.value);}}
                />
            </Form>
        </div>
    );
}

export { TimesComponent };