/* REACT */
import React from "react";
/* REDUX */
import { useAppDispatch, useAppSelector } from "../../../../../app/hooks";
/* ---- REDUCER ACTIONS ---- */
import {
  updateIsSaying,
  updateTellTarget,
} from "../../../../../features/chatInput/chatinput-slice";
/* TOOLTIPS */
import { Tooltip } from "react-tippy";
/* STYLES */
import "./styles.css";
/* CUSTOM COMPONENTS */
import SpeechBubble from "../../../../../components/SpeechBubble";

//ActionBar - Renders container for speech bubbles that act as "quick tell" button for all present NPCS
const ActionBar = ({
  presentAgents,
  getAgentName,
  getEntityId,
  dataModelHost,
}) => {
  /* REDUX DISPATCH FUNCTION */
  const dispatch = useAppDispatch();
  /* ------ REDUX STATE ------ */
  const persona = useAppSelector((state) => state.persona);
  return (
    <div className="actions">
      {/* {location ? <span>{location.name} &mdash; </span> : null} */}
      {presentAgents
        .filter((id) => id !== persona.id) // only show users other than self
        .map((agent) => {
          const agentName = getAgentName(agent);
          const agentId = getEntityId(agent);
          return (
            <span
              key={agentName}
              onClick={() => {
                dispatch(updateIsSaying(false));
                dispatch(updateTellTarget(agentName));
                //setTextTellAgent(agentName);
              }}
            >
              <Tooltip title={`tell ${agentName}...`} position="bottom">
                <SpeechBubble text={`${agentName}`} />
              </Tooltip>
              {dataModelHost && (
                <>
                  {" "}
                  <Tooltip
                    title={`suggest changes for ${agentName}`}
                    position="bottom"
                  >
                    <a
                      className="data-model-deep-link"
                      href={`${dataModelHost}/edit/${agentId}`}
                      rel="noopener noreferrer"
                      target="_blank"
                    >
                      <i className="fa fa-edit" aria-hidden="true" />
                    </a>
                  </Tooltip>
                </>
              )}
            </span>
          );
        })}
    </div>
  );
};

export default ActionBar;
