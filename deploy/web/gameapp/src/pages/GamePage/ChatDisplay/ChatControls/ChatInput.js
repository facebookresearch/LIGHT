import React from "react";

const ChatInput = ({
  onSubmit,
  enteredText,
  setEnteredText,
  chatInputRef,
  scrollToBottom,
}) => {
  return (
    <form
      style={{ display: "flex" }}
      onSubmit={(e) => {
        e.preventDefault();

        if (!!enteredText) {
          onSubmit(enteredText);
          setEnteredText("");
          scrollToBottom();
        }
      }}
    >
      <input
        className="chatbox-input"
        ref={chatInputRef}
        value={enteredText}
        onChange={(e) => setEnteredText(e.target.value)}
        onKeyPress={(e) => {
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
  );
};

export default ChatInput;
