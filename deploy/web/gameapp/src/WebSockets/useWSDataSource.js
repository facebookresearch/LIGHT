/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React, {
  useState,
  useEffect,
  useRef,
  useCallback,
  useReducer,
} from "react";

// Generates a random id
function uuidv4() {
  return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, function (c) {
    var r = (Math.random() * 16) | 0,
      v = c === "x" ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}

// MESSAGE REDUCER
const reducer = (state, msg) => {
  window.parent.postMessage(JSON.stringify(msg), "*");
  if (
    msg.text &&
    msg.text.indexOf("You mumble something incomprehensible") >= 0
  ) {
    let { event_id } = msg;
    const updatedState = state.map((message) => {
      if (event_id === message.event_id) {
        return msg;
      } else {
        return message;
      }
    });
    return updatedState;
  }
  if (msg.text.indexOf("Quest Complete:") >= 0) {
    const { text } = msg;
    let questExpIndex = text.indexOf("experience");
    let questExp = parseInt(text.slice(questExpIndex - 4, questExpIndex));
    let updatedQuestMsg = { ...msg, xp: questExp, questComplete: true };
    const updatedState = [...state, updatedQuestMsg];
    return updatedState;
  }
  if (
    (msg.caller === "SystemMessageEvent" && msg.text.indexOf("XP") >= 0) ||
    (msg.caller === "RewardEvent" && msg.text.indexOf("XP") >= 0)
  ) {
    console.log("EXP MESSAGE", msg);
    let { event_data } = msg;
    let {
      target_event, //UUID OF MESSAGE THAT TRIGGERED EXP
      reward, //XP AWARDED FROM BACKEND
    } = event_data;
    //MESSAGE BEFORE EXP
    let unUpdatedMsg = state.filter((message, index) => {
      return message.event_id === target_event;
    })[0];
    //MESSAGE WITH EXP
    let updatedMsg = { ...unUpdatedMsg, xp: unUpdatedMsg.exp + reward };
    //UPDATED MESSAGE PLACED IN PROPER POSITION IN STATE
    let updatedState = state.map((message) => {
      if (message.event_id === target_event) {
        return updatedMsg;
      }
      return message;
    });
    return updatedState;
  }
  const updatedState = [...state, msg];
  console.groupCollapsed("New message. Total: " + updatedState.length);
  console.table(updatedState);
  console.groupEnd();
  return updatedState;
};

/*
    Concatentates a list of items with an oxford style comma
    If the items is empty, returns the default message instead
  */
const stringifyList = (listItems, defaultMsg) => {
  var res = "";
  for (let i = 0; i < listItems.length; i++) {
    if (i === 0) {
      res += listItems[i];
    } else if (i === listItems.length - 1) {
      res += ", and " + listItems[i];
    } else {
      res += ", " + listItems[i];
    }
  }
  if (res === "") {
    return defaultMsg;
  }
  return res;
};

/*
    Get the labels on paths from neighbors, and display them on screen
  */
const getNeighbors = (action) => {
  var paths = [];
  Object.keys(action.room.neighbors).forEach((neighbor_id) => {
    var neighbor = action.room.neighbors[neighbor_id];
    paths.push(neighbor.label);
  });
  return stringifyList(paths, "there are no exits");
};

/*
    Get the objects in the room to display them
  */
const getItems = (action) => {
  var objects = [];
  Object.keys(action.objects).forEach((object_id) => {
    const object = action.objects[object_id];
    objects.push(object);
  });
  return stringifyList(objects, "nothing of interest");
};

//
export function useWSDataSource(url) {
  /*---------------STATE----------------*/
  const [isConnected, setConnected] = useState(false);
  const [isErrored, setErrored] = useState(false);
  const [isIdle, setIsIdle] = useState(false);
  const [isFull, setFull] = useState(false);
  const [persona, setPersona] = useState(null);
  const [location, setLocation] = useState(null);
  const [agents, setAgents] = useState({});
  const [aliveInterval, setAliveInterval] = useState(null);
  /*---------------REFS----------------*/
  const websocket = useRef();
  const agentList = useRef(agents);
  /*---------------REDUCERS----------------*/
  const [messages, appendMessage] = useReducer(reducer, []);

  agentList.current = agents;

  const handleMessage = useCallback(
    (msg) => {
      const cmd = JSON.parse(msg.data);
      if (cmd.command === "actions") {
        const buffer = [];

        cmd.data.forEach((action) => {
          const isPersonaDescription = action.caller === "SoulSpawnEvent";
          const isLocationDescription = action.caller === "LookEvent";
          action.room = JSON.parse(action.room);
          action.actor = JSON.parse(action.actor);
          var new_agents = {
            ...agentList.current,
            ...action.present_agent_ids,
          };
          setAgents(new_agents);
          if (isPersonaDescription) {
            setPersona({
              name: action.actor.name,
              description: action.actor.persona,
              id: action.actor.node_id,
              prefix: action.actor.name_prefix,
              xp: action.actor.xp,
              giftXp: action.actor.reward_xp,
            });
          }
          const neighbors = getNeighbors(action);
          const items = getItems(action);
          setLocation({
            name: action.room.name,
            description:
              action.room.desc +
              "\n" +
              "There is " +
              items +
              "." +
              "\n" +
              "You notice " +
              neighbors +
              ".",
            id: action.room.node_id,
          });
          buffer.push(action);
          buffer.forEach((msg) => appendMessage(msg));
        });
      } else if (cmd.command === "fail_find") {
        setFull(true);
      }
    },
    [appendMessage, setPersona, setAgents, setLocation]
  );

  useEffect(() => {
    websocket.current.onmessage = handleMessage;
  }, [handleMessage]);

  const submitMessage = useCallback(
    (txt) => {
      let event_id = uuidv4();
      appendMessage({
        caller: "say",
        text: txt,
        event_id: event_id,
        is_self: true,
        actors: [persona.id],
        exp: 0,
      });

      const msg = JSON.stringify({
        command: "act",
        data: { text: txt, event_id: event_id },
      });
      return websocket.current.send(msg);
    },
    [websocket, appendMessage, persona]
  );

  if (!websocket.current) {
    websocket.current = new WebSocket(url);

    // websocket.current.onmessage = handleMessage;

    websocket.current.onopen = () => {
      setConnected(true);
      const hb = JSON.stringify({ command: "hb", data: {} });
      var interval = window.setInterval(() => {
        websocket.current.send(hb);
      }, 10000);
      setAliveInterval(interval);
    };

    websocket.current.onerror = websocket.current.onclose = (e) => {
      console.log("errored", e);
      setConnected(false);
      setErrored(true);
      websocket.current = null;
      window.clearInterval(aliveInterval);
    };
  }
  const disconnectFromSession = () => {
    setConnected(false);
    websocket.current = null;
  };
  const markPlayerAsIdle = () => {
    setIsIdle(true);
  };
  return {
    isConnected,
    messages,
    submitMessage,
    persona,
    location,
    isErrored,
    agents,
    isFull,
    disconnectFromSession,
    markPlayerAsIdle,
    isIdle,
  };
}
