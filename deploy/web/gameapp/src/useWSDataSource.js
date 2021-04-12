import React from "react";

const reducer = (state, msg) => {
  // TODO replace the specific incomprehensible message somehow instead
  if (
    msg.text &&
    msg.text.startsWith("You mumble something incomprehensible")
  ) {
    let last_message = state[state.length - 1];
    if (last_message.is_self) {
      const slicedState = [...state.slice(0, state.length - 1), msg];
      console.groupCollapsed(
        "New message overwritten old. Total: " + slicedState.length
      );
      console.table(slicedState);
      console.groupEnd();
      return slicedState;
    }
  }
  if (msg.caller === "SystemMessageEvent" && msg.text.indexOf("XP") >= 0) {
    let i;
    for (i = state.length - 1; i > 0; i--) {
      let lastMessage = state[i];
      if (lastMessage.caller === "say" && lastMessage.is_self) {
        let messageWithExp = lastMessage.text.concat(msg.text);
        let filteredState = state.filter((message, index) => index != i);
        const updatedState = [...filteredState, messageWithExp];
        console.log(updatedState);
        return updatedState;
      }
    }
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

export function useWSDataSource(url) {
  const websocket = React.useRef();
  const [isConnected, setConnected] = React.useState(false);
  const [isErrored, setErrored] = React.useState(false);
  const [isFull, setFull] = React.useState(false);
  const [messages, appendMessage] = React.useReducer(reducer, []);
  const [persona, setPersona] = React.useState(null);
  const [location, setLocation] = React.useState(null);
  const [agents, setAgents] = React.useState({});
  const agentList = React.useRef(agents);
  agentList.current = agents;

  const handleMessage = React.useCallback(
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
              "\n" +
              "You notice " +
              neighbors,
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

  React.useEffect(() => {
    websocket.current.onmessage = handleMessage;
  }, [handleMessage]);

  const submitMessage = React.useCallback(
    (txt) => {
      appendMessage({
        caller: "say",
        text: txt,
        is_self: true,
        actors: [persona.id],
      });

      const msg = JSON.stringify({ command: "act", data: txt });
      return websocket.current.send(msg);
    },
    [websocket, appendMessage, persona]
  );

  if (!websocket.current) {
    websocket.current = new WebSocket(url);

    // websocket.current.onmessage = handleMessage;

    websocket.current.onopen = () => {
      console.log("opened");
      setConnected(true);
    };

    websocket.current.onerror = websocket.current.onclose = (e) => {
      console.log("errored", e);
      setConnected(false);
      setErrored(true);
      websocket.current = null;
    };
  }

  return {
    isConnected,
    messages,
    submitMessage,
    persona,
    location,
    isErrored,
    agents,
    isFull,
  };
}
