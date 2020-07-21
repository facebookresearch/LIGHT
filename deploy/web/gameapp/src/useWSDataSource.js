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
          const isRespawn = false; /* action.text.startsWith(
            "Your lost soul attempts to join the living..."
          );*/
          const isPersonaDescription = action.caller === "SpawnEvent";
          const isLocationDescription = action.caller === "LookEvent";
          const hasUpdatedAgentsInfo = true; 
          action.room = JSON.parse(action.room)
          action.actor = JSON.parse(action.actor)

          if (hasUpdatedAgentsInfo) {
            setAgents(
                action.present_agent_ids
            );
          }
          if (isPersonaDescription) {
            setPersona({
              name: action.actor.name,
              description: action.actor.persona,
              id: action.actor.node_id
            });
            if (isRespawn) {
              buffer.push(action);
            }
            return;
          } else if (isLocationDescription) {
            setLocation({
              name: action.room.name,
              description:
                action.room.desc +
                "\n" +
                "You notice: " +
                "TODO add examine stuff here" + 
                ".",
              id: action.room.node_id
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
