/* REACT */
import React, {useState, useCallback, useEffect} from 'react';

import { Typeahead, TypeaheadInputMulti } from 'react-bootstrap-typeahead';

import Token from "./Token"

const TypeAheadTokenizerForm = ({
    formLabel,
    options
})=>{
    const [selected, setSelected] = useState([]);

    const onMove = useCallback(
      (dragIndex, hoverIndex) => {
        const item = selected[dragIndex];
  
        const newSelected = selected.slice();
        newSelected.splice(dragIndex, 1);
        newSelected.splice(hoverIndex, 0, item);
  
        setSelected(newSelected);
      },
      [selected]
    );

    return(
        <div>
            <h5>{formLabel}</h5>
            <Typeahead
                id="dnd-token-example"
                multiple
                onChange={setSelected}
                options={options}
                placeholder="Choose a state..."
                renderInput={(inputProps, props) => (
                    <TypeaheadInputMulti {...inputProps} selected={selected}>
                        {selected.map((option, idx) => (
                            <Token
                                index={idx}
                                key={option.label}
                                onMove={onMove}
                                onRemove={props.onRemove}
                                option={option}>
                                {option.label}
                            </Token>
                        ))}
                    </TypeaheadInputMulti>
                )}
                selected={selected}
      />
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