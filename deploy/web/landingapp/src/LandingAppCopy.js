const LandingAppCopy = {
  terminalDialogue: [
    {
      text:
        "After arriving on this page, you find yourself transported to a new world… ",
      highlighted: false,
    },
    {
      text: "> Look around",
      highlighted: true,
    },
    {
      text:
        "You can’t really make out much of anything near you. It’s almost as if it’s all a blur, or like you’re suspended underwater. One spot of clarity in the noise: a figure in a cloak gestures in your direction.",
      highlighted: false,
    },
    {
      text: "> “Hello…?”",
      highlighted: true,
    },
    {
      text:
        "“Welcome to LIGHT, my friend,” it says. “Beyond here is a world of strange characters, interesting locations, and goals to achieve, all serving to help out with AI research on conversational language understanding. Are you interested in participating?”",
      highlighted: false,
    },
    {
      text:
        "“Alright then, perhaps some other time,” the figure responds, before vanishing entirely. The page is now static, but still links to the FAQ and Terms pages.",
      highlighted: false,
    },
  ],
  legalAgreements: [],
  introDialogueSteps: [
    {
      action: "say",
      actor: "Dungeon Master",
      text: "Welcome to Light.",
      isSelf: false,
    },
    {
      action: "say",
      actor: "Dungeon Master",
      text: "Try saying hello using the chat bar.",
      isSelf: false,
    },
    {
      action: "say",
      actor: "Dungeon Master",
      text:
        "Well done!  Toggle between saying and doing using the chat button or pressing the ` key.  Try doing something.",
      isSelf: false,
    },
    {
      action: "say",
      actor: "Dungeon Master",
      text:
        "Well done!  You can like and dislike messages.  Try clicking on a rating system.",
      isSelf: false,
    },
    {
      action: "say",
      actor: "Dungeon Master",
      text: "Great job you are now ready to enter the world of light.",
      isSelf: false,
    },
  ],
};
export default LandingAppCopy;
