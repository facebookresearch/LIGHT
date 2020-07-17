import React from "react";
import ReactDOM from "react-dom";

import "./styles.css";
import "react-tippy/dist/tippy.css";
import "emoji-mart/css/emoji-mart.css";

import { Tooltip } from "react-tippy";
import { Picker, emojiIndex } from "emoji-mart";
import cx from "classnames";
import onClickOutside from "react-onclickoutside";

import { useWSDataSource } from "./useWSDataSource";
import Logo from "./Logo";
import LoadingScreen from "./LoadingScreen";

import { setCaretPosition } from "./utils";

import CONFIG from "./config";

const createWebSocketUrlFromBrowserUrl = (url) => {
  const wsProtocol = url.protocol === "https:" ? "wss" : "ws";
  const optionalServerHost = new URL(url).searchParams.get("server");
  var optionalGameId = new URL(url).searchParams.get("id");
  if (!optionalGameId){
    optionalGameId = "";
  }
  if (optionalServerHost) {
    console.log("Using user-provided server hostname:", optionalServerHost);
  }
  const websocketURL =
    wsProtocol + "://" + (optionalServerHost || CONFIG.hostname) + ":" + CONFIG.port + `/game${optionalGameId}/socket`;
  return websocketURL;
};

const getDataModelAddress = () => {
  return new URL(window.location).searchParams.get("builder");
};

// TODO: consider showing different agent's dialogues in
// different colors
//
// const colors = [
//   "#edfff1", //green,
//   "#fffded", //yellow,
//   "#eee8ff", // purple
//   "#e6efff", //blue
//   "#ffe8eb" //red
// ];

function Setting(props) {
  return (
    <div style={{ clear: "both", overflow: "auto" }}>
      <div className="message type-setting">
        {props.text.split("\n").map((para, idx) => (
          <p key={idx}>{para}</p>
        ))}
      </div>
    </div>
  );
}

function Message({ text, caller, actor, isSelf, onReply }) {
  const [isEditMode, setEditMode] = React.useState(false);

  let classNames = "message type-dialogue ";
  if (["tell", "say", "whisper"].includes(caller)) {
    text = "&ldquo;" + text + "&rdquo;";
    classNames = "message type-dialogue ";
  }
  classNames += isSelf ? "me" : "other";

  if (isEditMode) {
    return (
      <div className={classNames}>
        <div className="agent">
          <span>{actor}</span>
          {isSelf ? null : (
            <React.Fragment>
              <i className="fa fa-reply" onClick={() => onReply(actor)} />{" "}
              <i
                className="fa fa-commenting-o "
                onClick={() => setEditMode(true)}
              />
            </React.Fragment>
          )}
        </div>
        <div style={{ opacity: 0, height: 1, pointerEvents: "none" }}>
          {text}
        </div>
        <input className="edit-message" defaultValue={text} />
        <button type="submit" onClick={() => setEditMode(false)}>
          Suggest edit
        </button>
      </div>
    );
  }

  return (
    <div className={classNames}>
      <div className="agent">
        <span>{actor}</span>
        {isSelf ? null : (
          <React.Fragment>
            <Tooltip title={`tell ${actor}...`} position="top">
              <i className="fa fa-reply" onClick={() => onReply(actor)} />
            </Tooltip>{" "}
            <Tooltip
              title={`Do you think something else should have been said instead? Provide feedback via an edit...`}
              position="top"
            >
              <i
                className="fa fa-commenting-o "
                onClick={() => setEditMode(true)}
              />
            </Tooltip>
          </React.Fragment>
        )}
      </div>
      {text}
    </div>
  );
}

function Entry({ msg, onReply, agents, selfId }) {
  if (["LookEvent", "GoEvent", "ExamineEvent", "ErrorEvent", "HelpEvent", "text"].includes(msg.caller) || msg.caller === null) {
    return <Setting text={msg.text} />;
  } else {
    return (
      <Message
        text={msg.text}
        isSelf={msg.is_self || msg.actors[0] === selfId}
        actor={agents[msg.actors[0]]}
        onReply={onReply}
      />
    );
  }
}

function ConnectedApp() {
  const wsUrl = React.useMemo(
    () => createWebSocketUrlFromBrowserUrl(window.location),
    []
  );
  const {
    isErrored,
    messages,
    submitMessage,
    persona,
    location,
    agents
  } = useWSDataSource(wsUrl);

  if (isErrored)
    return (
      <div style={{ textAlign: "center", marginTop: 30, fontSize: 30 }}>
        Could not connect to the server.
      </div>
    );

  if (messages.length === 0) {
    return <LoadingScreen />;
  }

  return (
    <Chat
      messages={messages}
      onSubmit={submitMessage}
      persona={persona}
      // persona={{ name: "a cow" }}
      location={location}
      agents={agents}
    />
  );
}
function Chat({ messages, onSubmit, persona, location, agents }) {
  const [enteredText, setEnteredText] = React.useState("");
  const chatContainerRef = React.useRef(null);
  const getAgentName = agent => (agents ? agents[agent] : agent);
  const getEntityId = agent => agent.match(/\d+$/)[0];
  const dataModelHost = getDataModelAddress();

  const scrollToBottom = React.useCallback(
    () =>
      setTimeout(() => {
        if (chatContainerRef.current)
          chatContainerRef.current.scrollTop =
            chatContainerRef.current.scrollHeight;
      }, 0),
    [chatContainerRef]
  );

  React.useEffect(() => {
    scrollToBottom();
  }, [scrollToBottom, messages]);

  const defaultEmoji = "❓";
  const { presentAgents } = getLocationState(messages);
  const [showEmojiPicker, setShowEmojiPicker] = React.useState(false);
  const [selectedEmoji, setSelectedEmoji] = React.useState(defaultEmoji);

  const chatInputRef = React.useRef();
  React.useLayoutEffect(() => {
    chatInputRef.current.focus();
  }, []);

  React.useEffect(() => {
    if (persona === null || persona.name === null) return;
    const skipWords = ["a", "the", "an", "of", "with", "holding"];
    const tryPickEmojis = !persona
      ? []
      : persona.name
          .split(" ")
          .filter(token => !!token)
          .map(token => token.replace(/\.$/, ""))
          .filter(word => skipWords.indexOf(word.toLowerCase()) === -1)
          .flatMap(term =>
            emojiIndex.search(term).map(o => {
              return o.native;
            })
          );

    const autopickedEmoji =
      tryPickEmojis.length > 0 ? tryPickEmojis[0] : defaultEmoji;
    setSelectedEmoji(autopickedEmoji);
  }, [persona, setSelectedEmoji]);

  const setTextTellAgent = React.useCallback(
    agent => {
      const message = `tell ${agent} ""`;
      setEnteredText(message);
      setTimeout(
        () => setCaretPosition(chatInputRef.current, message.length - 1),
        0 /* 0s timeout to schedule this task to occur after the layout is updated */
      );
    },
    [setEnteredText, chatInputRef]
  );

  // console.log(selectedEmoji);
  return (
    <div className="App">
      <div className="sidebar">
        <Logo />
        <div className="game-state">
          {persona ? (
            <div className="persona">
              <div
                className={cx("icon", { editing: showEmojiPicker })}
                style={{ cursor: "pointer" }}
              >
                <div className="overlay">edit</div>
                <span
                  role="img"
                  aria-label="avatar"
                  onClick={() => setShowEmojiPicker(true)}
                >
                  {selectedEmoji}
                </span>
                {showEmojiPicker ? (
                  <div
                    style={{
                      position: "absolute",
                      top: "80px",
                      left: "50%",
                      transform: "translateX(-50%)",
                      zIndex: 999
                    }}
                  >
                    <BlurClosingPicker
                      autoFocus={true}
                      onBlur={() => setShowEmojiPicker(false)}
                      onSelect={emoji => {
                        // TODO: Send the selected emoji to the back-end so we can keep record it
                        setSelectedEmoji(emoji.native);
                        setShowEmojiPicker(false);
                      }}
                    />
                  </div>
                ) : null}
              </div>
              <h3>You are {persona.name}</h3>
              {persona.description}
              {dataModelHost && (
                <Tooltip
                  style={{ position: "absolute", bottom: 0, right: 5 }}
                  title={`suggest changes for ${persona.name}`}
                  position="bottom"
                >
                  <a
                    className="data-model-deep-link"
                    href={`${dataModelHost}/edit/${getEntityId(persona.id)}`}
                    rel="noopener noreferrer"
                    target="_blank"
                  >
                    <i className="fa fa-edit" aria-hidden="true" />
                  </a>
                </Tooltip>
              )}
            </div>
          ) : null}
          {location ? (
            <div className="location">
              <h3>{location.name}</h3>
              {location.description.split("\n").map((para, idx) => (
                <p key={idx}>{para}</p>
              ))}
              {dataModelHost && (
                <Tooltip
                  style={{ position: "absolute", bottom: 0, right: 5 }}
                  title={`suggest changes for ${
                    location.name.split(" the ")[1]
                  }`}
                  position="bottom"
                >
                  <a
                    className="data-model-deep-link"
                    href={`${dataModelHost}/edit/${getEntityId(location.id)}`}
                    rel="noopener noreferrer"
                    target="_blank"
                  >
                    <i className="fa fa-edit" aria-hidden="true" />
                  </a>
                </Tooltip>
              )}
            </div>
          ) : null}
        </div>
        {/* <Map /> */}
        {/* <div className="app-controls">
          <label>
            <input
              type="checkbox"
              checked={isAdminMode}
              onChange={e => setAdminMode(!isAdminMode)}
            />{" "}
            Admin Mode
          </label>
        </div> */}
      </div>
      <div className="chat-wrapper">
        <div className="chat" ref={chatContainerRef}>
          <div className="chatlog">
            {messages.map((msg, idx) => (
              <Entry
                key={idx}
                msg={msg}
                agents={agents}
                onReply={agent => setTextTellAgent(agent)}
                selfId={persona.id}
              />
            ))}
          </div>
        </div>
        <div className="controls">
          <form
            style={{ display: "flex" }}
            onSubmit={e => {
              e.preventDefault();

              if (!!enteredText) {
                onSubmit(enteredText);
                setEnteredText("");
                scrollToBottom();
              }
            }}
          >
            <input
              ref={chatInputRef}
              value={enteredText}
              onChange={e => setEnteredText(e.target.value)}
              onKeyPress={e => {
                if (e.key === "Enter" && e.shiftKey) {
                  const prefix = e.target.value.startsWith('"') ? "" : '"';
                  const suffix = e.target.value.endsWith('"') ? "" : '"';
                  setEnteredText(prefix + e.target.value + suffix);
                }
              }}
              className="chatbox"
              placeholder="Enter text to interact with the world here..."
            />
          </form>
          <div className="actions">
            <div style={{ float: "left" }}>
              {/* {location ? <span>{location.name} &mdash; </span> : null} */}
              {presentAgents
                .filter(id => id !== persona.id) // only show users other than self
                .map(agent => {
                  const agentName = getAgentName(agent);
                  const agentId = getEntityId(agent);
                  return (
                    <span
                      key={agentName}
                      style={{
                        backgroundColor: "#eee",
                        borderRadius: 3,
                        padding: "1px 3px",
                        marginRight: 5
                      }}
                    >
                      <span
                        onClick={() => {
                          setTextTellAgent(agentName);
                        }}
                      >
                        {agentName}{" "}
                        <Tooltip
                          title={`tell ${agentName}...`}
                          position="bottom"
                        >
                          <i className="fa fa-comment-o" aria-hidden="true" />
                        </Tooltip>
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
                    </span>
                  );
                })}
            </div>

            <div
              style={{
                display: "flex",
                alignItems: "center",
                float: "right"
              }}
            >
              <span
                className={cx("hint-message", "fadeHidden", {
                  fadeShow: enteredText.length > 0 && enteredText[0] === '"'
                })}
              >
                Tip: Hit Shift+Enter to auto-wrap your entry in quotes
              </span>
            </div>

            {[
              // "act",
              // "say",
              // "tell"
              // "whisper",
              // "applaud",
              // "blush",
              // "cry",
              // "dance",
              // "frown",
              // "gasp",
              // "grin",
              // "groan",
              // "growl",
              // "laugh",
              // "nod",
              // "nudge",
              // "ponder",
              // "pout",
              // "scream",
              // "shrug",
              // "sigh",
              // "smile",
              // "stare",
              // "wave",
              // "wink",
              // "yawn"
            ].map(action => (
              <span className="action" key={action}>
                {action}
              </span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

const EmojiPicker = ({ onBlur, ...props }) => {
  EmojiPicker.handleClickOutside = () => onBlur();
  return <Picker {...props} />;
};
const BlurClosingPicker = onClickOutside(EmojiPicker, {
  handleClickOutside: () => EmojiPicker.handleClickOutside
});

const rootElement = document.getElementById("root");
ReactDOM.render(<ConnectedApp />, rootElement);

function getLocationState(messages) {
  var valid_messages = messages.filter(
    m => m.is_self !== true && m.caller !== null
  );
  if (valid_messages.length === 0) return [null, []];
  var lastMessage = valid_messages[valid_messages.length - 1];

  return {
    currentRoom: lastMessage.room_id,
    presentAgents: lastMessage.present_agent_ids
  };
}
