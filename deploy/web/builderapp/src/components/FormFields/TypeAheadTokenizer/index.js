import React, { useCallback, useState, useEffect } from 'react';
import { Typeahead, TypeaheadInputMulti } from 'react-bootstrap-typeahead';
import { DndProvider } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';

import Token from './Token';

import options from './dummyTokenOptionData';

import 'react-bootstrap-typeahead/css/Typeahead.css';
import './styles.css';
import { BsGear } from 'react-icons/bs';

const TypeaheadTokenizer = ({
    formLabel,
    tokenOptions,
    worldId,
    sectionName,
    roomId,
    tokens,
    onTokenAddition,
    onTokenRemoval
}) => {
    const [tokenList, setTokenList] = useState([]);
    const [selected, setSelected] = useState([]);
    useEffect(() => {
       if(tokens){
        console.log("DEFAULT TOKENS", tokens)
        let updatedtokens = tokens.map((tokendata, index)=>{
            let updatedDefaultTokenData = {
                index: index,
                label: tokendata.name,
                key: tokendata.node_id,
                data: tokendata
            }
            return updatedDefaultTokenData;
        })
        setSelected([...updatedtokens]) 
       }else{
        setSelected([]) 
       }
    }, [tokens, roomId])
    useEffect(() => {
        if(tokenOptions.length){
            console.log("TOKEN OPTIONS    ", tokenOptions)
            let updatedTokenList = tokenOptions.map((tokendata, index)=>{
                let updatedTokenData = {
                    index: index,
                    label: tokendata.name,
                    key: tokendata.node_id,
                    data: tokendata
                }
                return updatedTokenData;
            })
            setTokenList(updatedTokenList)
        }
    }, [tokenOptions])

console.log(formLabel, tokenOptions)
const SelectHandler = (selected)=>{
    console.log("SELECTED:  ",selected);
    let newSelection = selected[selected.length-1].data
    onTokenAddition(newSelection)
}

  return (
    <DndProvider backend={HTML5Backend}>
        <h5>
            {formLabel}
        </h5>
        <Typeahead
            id="typeahead-tokenizer"
            allowNew={true}
            multiple
            onChange={SelectHandler}
            selected={selected}
            options={tokenList}
            placeholder="Select one"
            renderInput={(inputProps, props) => (
            <TypeaheadInputMulti {...inputProps} selected={selected}>
                {selected.map((option, idx) => (
                    <Token
                        index={idx}
                        option={option}
                        key={option.key}
                        worldId={worldId}
                        sectionName={sectionName}
                        roomId={roomId}
                    >   
                        {option.label.toUpperCase()}
                    </Token>
                ))}
            </TypeaheadInputMulti>
            )}
        />
    </DndProvider>
  );
};


export default TypeaheadTokenizer;