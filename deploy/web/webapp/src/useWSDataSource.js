import React from "react";
import { zipToObject } from "./utils";

const reducer = (state, msg) => {
  const updatedState = [...state, msg];
  console.groupCollapsed("New message. Total: " + updatedState.length);
  console.table(updatedState);
  console.groupEnd();
  return updatedState;
};

export function useWSDataSource(url) {
  const websocket = React.useRef();
  const [isConnected, setConnected] = React.useState(false);
  const [isErrored, setErrored] = React.useState(false);
  const [messages, appendMessage] = React.useReducer(reducer, []);
  const [persona, setPersona] = React.useState(null);
  const [location, setLocation] = React.useState(null);
  const [agents, setAgents] = React.useState({});

  const handleMessage = React.useCallback(
    msg => {
      const cmd = JSON.parse(msg.data);
      if (cmd.command === "actions") {
        const buffer = [];

        cmd.data.forEach(action => {
          const isRespawn = action.text.startsWith(
            "Your lost soul attempts to join the living..."
          );
          const isPersonaDescription =
            action.caller === null && action.name === "persona";
          const isLocationDescription = action.name === "list_room";
          const hasUpdatedAgentsInfo = !!action.room_agents;

          if (hasUpdatedAgentsInfo) {
            setAgents(
              zipToObject(action.room_agents[0], action.room_agents[1])
            );
          }
          if (isPersonaDescription) {
            setPersona({
              name: action.character,
              description: action.persona,
              id: action.actors[0]
            });
            if (isRespawn) {
              buffer.push(action);
            }
            return;
          } else if (isLocationDescription) {
            const locationName = action.text.split("\n")[0];
            setLocation({
              name: locationName,
              description:
                action.room_desc +
                "\n" +
                "You notice: " +
                action.room_descs.join(", ") +
                ".",
              id: action.room_id
            });
            buffer.push(action);
          } else {
            buffer.push(action);
          }

          buffer.forEach(msg => appendMessage(msg));
        });
      }
    },
    [appendMessage, setPersona, setAgents, setLocation]
  );

  React.useEffect(() => {
    websocket.current.onmessage = handleMessage;
  }, [handleMessage]);

  const submitMessage = React.useCallback(
    txt => {
      appendMessage({
        caller: "say",
        text: txt,
        is_self: true,
        actors: [persona.id]
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
    agents
  };
}
