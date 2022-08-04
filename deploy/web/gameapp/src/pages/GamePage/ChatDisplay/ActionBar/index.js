/* REACT */
import React from "react";
/* REDUX */
import { useAppDispatch, useAppSelector } from "../../../../app/hooks";
import { updateSelectedTip } from "../../../../features/tutorials/tutorials-slice";
/* ---- REDUCER ACTIONS ---- */
import {
  updateIsSaying,
  updateTellTarget,
} from "../../../../features/chatInput/chatinput-slice";
/* TOOLTIPS */
import { Tooltip } from "react-tippy";
/* STYLES */
import "./styles.css";
/* CUSTOM COMPONENTS */
import SpeechBubble from "../../../../components/SpeechBubble";
import TutorialPopover from "../../../../components/TutorialPopover";

//ActionBar - Renders container for speech bubbles that act as "quick tell" button for all present NPCS
const ActionBar = ({
  presentAgents,
  getAgentName,
  getEntityId,
  dataModelHost,
}) => {
  /* ------ REDUX STATE ------ */
  const inHelpMode = useAppSelector((state) => state.tutorials.inHelpMode);
  const selectedTip = useAppSelector((state) => state.tutorials.selectedTip);
  const persona = useAppSelector((state) => state.persona);
  /* ----REDUX ACTIONS---- */
  // REDUX DISPATCH FUNCTION
  const dispatch = useAppDispatch();
  const setSelectedTip = (tipNumber) => {
    if (inHelpMode) {
      dispatch(updateSelectedTip(tipNumber));
    }
  };
  return (
    <div
      className={`actions flex flex-col flex-start ${
        inHelpMode ? "active" : ""
      }`}
      onClick={() => setSelectedTip(8)}
    >
      <p className="text-gray-200">{`Characters present in ${"location"}`}</p>
      <TutorialPopover
        tipNumber={8}
        open={inHelpMode && selectedTip === 8}
        position="bottom"
      ></TutorialPopover>
      {/* {location ? <span>{location.name} &mdash; </span> : null} */}
      <div className=" ">
        {presentAgents
          .filter((id) => id !== persona.id) // only show users other than self
          .map((agent) => {
            const agentName = getAgentName(agent);
            const agentId = getEntityId(agent);
            return (
              <span
                key={agentName}
                onClick={() => {
                  if (!inHelpMode) {
                    dispatch(updateIsSaying(false));
                    dispatch(updateTellTarget(agentName));
                  }
                }}
              >
                <Tooltip title={`tell ${agentName}...`} position="bottom">
                  <button
                    type="button"
                    className="inline-flex items-center px-2.5 py-1.5 border border-gray-300 shadow-sm text-xs font-medium rounded text-gray-200 bg-transparent hover: bg-gray-800 "
                  >
                    {`${agentName}`}
                  </button>
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
    </div>
  );
};

export default ActionBar;
