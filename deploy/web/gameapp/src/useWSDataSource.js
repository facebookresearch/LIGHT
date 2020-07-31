import React from "react";

const reducer = (state, msg) => {
  const updatedState = [...state, msg];
  console.groupCollapsed("New message. Total: " + updatedState.length);
  console.table(updatedState);
  console.groupEnd();
  return updatedState;
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
  var notice = "";
  for (let i = 0; i < paths.length; i++) {
    if (i === 0) {
      notice += paths[i];
    } else if (i === paths.length - 1) {
      notice += ", and " + paths[i];
    } else {
      notice += ", " + paths[i];
    }
  }
  if (notice === "") {
    notice = "there are no exits";
  }
  return notice;
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

  var items = "";
  for (let i = 0; i < objects.length; i++) {
    if (i === 0) {
      items += objects[i];
    } else if (i === objects.length - 1) {
      items += ", and " + objects[i];
    } else {
      items += ", " + objects[i];
    }
  }
  if (items === "") {
    items = "nothing of interest.";
  }
  return items;
};

export function useWSDataSource(url) {
  const websocket = React.useRef();
  const [isConnected, setConnected] = React.useState(false);
  const [isErrored, setErrored] = React.useState(false);
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

    websocket.current.onerror = websocket.current.onclose = () => {
      console.log("errored");
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
  };
}
