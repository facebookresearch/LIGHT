/* REDUX */
import { createSlice, PayloadAction } from "@reduxjs/toolkit";
/* CUSTOM TYPES */

interface ContainerNode {
    target_id: String;
}

interface ContainerNodes {
    [key: string]: ContainerNode;
}

interface Event {

}

interface Neighbor {
    examine_desc: string;
    label: string;
    locked_edge: any;
    target_id: string;
}

interface Neighbors {
    [key: string]: Neighbor;
}


interface Character {
    agent: Boolean;
    usually_npc: Boolean;
    aggression: Number;
    char_type: String;
    classes: Array<String>;
    contain_size: Number;
    contained_nodes: ContainerNodes;
    damage: Number;
    db_id: String | null;
    defense: Number;
    desc: String;
    followed_by: any;
    following: any | null;
    food_energy: Number;
    health: Number;
    is_player: Boolean;
    name: String;
    name_prefix: String;
    names: Array<String>;
    node_id: String;
    object: Boolean;
    plural: String|null;
    tags: Array<String>;
    attack_tagged_agents:Array<String>;
    dont_accept_gifts: Boolean;
    on_events: Array<Array<Array<String>>>;
    persona: String;
    room: Boolean;
    size: Number;
    speed: Number;
  }

/* STATE TYPE */
interface WorldCharactersState {
  worldCharacters: Array<Character>;
  selectedCharacter: Character | null;
}

/* Initial value of the state */
const initialState: WorldCharactersState = {
    worldCharacters: [],
    selectedCharacter: null
};

//Create slice will generate action objects for us
const worldCharactersSlice = createSlice({
  name: "worldCharacters",
  initialState,
  /* REDUCER ACTIONS */
  reducers: {
        updateCharacters(state, action: PayloadAction<Array<Character>>){
            return {
                ...state,
                worldCharacters: action.payload
            }
        },
        selectCharacter(state, action: PayloadAction<Character>) {
            return {
                ...state,
                selectedCharacter: action.payload,
            };
        },
        updateSelectedCharacter(state, action: PayloadAction<Character>) {
            return {
                ...state,
                selectedCharacter: action.payload,
            };
        },
        addCharacter(state, action: PayloadAction<Character>) {
            return {
                ...state,
                worldCharacters: [...state.worldCharacters, action.payload],
            };
        },
        removeCharacter(state, action: PayloadAction<string>) {
            const updatedCharacters = state.worldCharacters.filter(character=>(character.node_id!==action.payload))
            return {
                ...state,
                worldCharacters: updatedCharacters,
            };
        },
    }
});

/* EXPORTED REDUCER ACTIONS */
// import anywhere in app to use
export const {
    updateCharacters,
    selectCharacter,
    updateSelectedCharacter,
    addCharacter,
    removeCharacter
} = worldCharactersSlice.actions;
/* SLICE REDUCER */
export default worldCharactersSlice.reducer;
