/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React, { useCallback, useState, useEffect } from 'react';
import { Typeahead, TypeaheadInputMulti } from 'react-bootstrap-typeahead';
import { DndProvider } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';

import Token from './Token';

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
    tokenType,
    onTokenAddition,
    onTokenRemoval
}) => {
    //LOCAL STATE
    const [tokenList, setTokenList] = useState([]);
    const [selected, setSelected] = useState([]);
    useEffect(() => {
       if(tokens){
        console.log("DEFAULT TOKENS", tokens)
        let updatedtokens = tokens.map((tokenData, index)=>{
            let updatedDefaultTokenData = {
                index: index,
                label: tokenData.name,
                key: tokenData.node_id,
                data: tokenData
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
    selected.map((selectedToken, index)=>{
        const {id, data, customOption, label}= selectedToken;


        let selectedUpdate
        if(index==(selected.length-1)){
            console.log("TOKEN TYPE:  ", tokenType, customOption)
                if( tokenType === 'characters'){
                    if(customOption){
                        let newCharacterTokenData = {
                            agent:true,
                            aggression:0,
                            attack_taggedAgents:[],
                            blocked_by:{},
                            blocking:null,
                            char_type:"person",
                            classes:["agent"],
                            contain_size: 0,
                            contained_nodes:{},
                            container_node:{target_id: roomId},
                            damage:1,
                            db_id:null,
                            dead:false,
                            defense:0,
                            desc:"",
                            dexterity:0,
                            dont_accept_gifts:false,
                            followed_by:{},
                            follow:null,
                            food_energy:1,
                            health:2,
                            is_player:false,
                            max_distance_from_start_location: 1000000,
                            max_wearable_items: 3,
                            max_wieldable_items:1,
                            mission: "",
                            movement_energy_cost: 0,
                            name:label,
                            name_prefix:"",
                            names:[label],
                            node_id: null,
                            num_wearable_items: 0,
                            num_wieldable_items: 0,
                            object:false,
                            on_events:[],
                            pacifist: false,
                            persona: "",
                            quests:[],
                            size:20,
                            speed:5,
                            strength: 0,
                            tags:[],
                            usually_npc:false
                        };
                        console.log("NEW CHAR DATA:  ", newCharacterTokenData)
                        let newCharacterToken = {
                            key:{label},
                            label: label,
                            data: newCharacterTokenData
                        }
                        console.log("NEW CHAR TOKEN DATA:  ", newCharacterToken)
                        selectedToken= newCharacterToken
                        console.log("NEW CHAR UPDATE:  ", selectedUpdate)
                    }else{
                        selectedUpdate= selectedToken
                        console.log("NEW CHAR UPDATE:  ", selectedUpdate)
                    }
                }
                if( tokenType === 'objects'){
                    console.log("OBJECTO:  ", selectedToken)
                    if(customOption){
                        let newObjectTokenData = {
                            agent:false,
                            classes:["object"],
                            contain_size: 0,
                            contained_nodes:{},
                            container: false,
                            container_node:{target_id: roomId},
                            db_id:null,
                            dead:false,
                            desc:"",
                            drink:false,
                            equipped:null,
                            food:false,
                            food_energy:0,
                            gettable:true,
                            locked_edge:null,
                            name:label,
                            name_prefix:"",
                            names:[label],
                            node_id: null,
                            object:true,
                            on_use:null,
                            room:false,
                            size:1,
                            stats:{damage:0, defense:0},
                            surface_type:"on",
                            value: 1,
                            wearable: false,
                            wieldable: false
                        };
                        let newObjectToken = {
                            key:{label},
                            label: label,
                            data: newObjectTokenData
                        }
                        selectedToken= newObjectToken
                    }
                }
            selectedUpdate= selectedToken
            console.log("ON TOKEN ADDITION DATA:  ", selectedUpdate)
            onTokenAddition(selectedUpdate.data)
        }
    })
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
                {selected.length ? selected.map((option, idx) => (
                    <Token
                        index={idx}
                        option={option}
                        key={option.key}
                        worldId={worldId}
                        sectionName={sectionName}
                        roomId={roomId}
                        deleteTokenFunction={onTokenRemoval}
                    >   
                        {option.label.toUpperCase()}
                    </Token>
                )):
                null}
            </TypeaheadInputMulti>
            )}
        />
    </DndProvider>
  );
};


export default TypeaheadTokenizer;