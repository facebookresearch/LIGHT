/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

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

import { RiReplyFill } from "react-icons/ri";

//ActionBar - Renders container for speech bubbles that act as "quick tell" button for all present NPCS
const ActionBar = ({
  presentAgents,
  getAgentName,
  getEntityId,
  dataModelHost,
  chatInputRef,
}) => {
  /* ------ REDUX STATE ------ */
  const inHelpMode = useAppSelector((state) => state.tutorials.inHelpMode);
  const selectedTip = useAppSelector((state) => state.tutorials.selectedTip);
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
      className={`_action-bar_ actions flex flex-col flex-start ${
        inHelpMode ? "active" : ""
      }`}
      onClick={() => setSelectedTip(8)}
    >
      <div className="text-base-100 opacity-60 text-xs mb-2">{`Characters present in ${"location"}`}</div>
      <TutorialPopover
        tipNumber={8}
        open={inHelpMode && selectedTip === 8}
        position="bottom"
      ></TutorialPopover>
      {/* {location ? <span>{location.name} &mdash; </span> : null} */}
      <div className="mb-4">
        {presentAgents.map((agent) => {
          const agentName = getAgentName(agent);
          const agentId = getEntityId(agent);
          return (
            <div
              key={agentName}
              className="btn btn-outline btn-sm btn-info capitalize"
              onClick={() => {
                if (!inHelpMode) {
                  dispatch(updateIsSaying(false));
                  dispatch(updateTellTarget(agentName));
                  chatInputRef.current.focus();
                }
              }}
            >
              <span className="inline-flex">
                <span className="pr-2">{`${agentName}`}</span> <RiReplyFill />
              </span>

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
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default ActionBar;
