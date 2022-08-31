/*****
 * Copyright (c) Meta Platforms, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React from "react";
/* REDUX */
import { useAppDispatch, useAppSelector } from "../../../../../app/hooks";
import { updateSelectedTip } from "../../../../../features/tutorials/tutorials-slice";
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
import TutorialPopover from "../../../../../components/TutorialPopover";

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
      className={`actions ${inHelpMode ? "active" : ""}`}
      onClick={() => setSelectedTip(8)}
    >
      <TutorialPopover
        tipNumber={8}
        open={inHelpMode && selectedTip === 8}
        position="top"
      ></TutorialPopover>
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
                if (!inHelpMode) {
                  dispatch(updateIsSaying(false));
                  dispatch(updateTellTarget(agentName));
                }
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
