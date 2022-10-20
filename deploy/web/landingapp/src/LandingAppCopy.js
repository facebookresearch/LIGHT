const LandingAppCopy = {
  terminalDialogue: [
    {
      text:
        "After arriving on this page, you find yourself transported to a new world… ",
      highlighted: false,
      step: 0,
    },
    {
      text: "> Look around",
      highlighted: true,
      step: 0,
    },
    {
      text:
        "You can’t really make out much of anything near you. It’s almost as if it’s all a blur, or like you’re suspended underwater. One spot of clarity in the noise: a figure in a cloak gestures in your direction.",
      highlighted: false,
      step: 1,
    },
    {
      text: "> “Hello…?”",
      highlighted: true,
      step: 1,
    },
    {
      text:
        "“Welcome to LIGHT, my friend,” it says. “Beyond here is a world of strange characters, interesting locations, and goals to achieve, all serving to help out with AI research on conversational language understanding. Are you interested in participating?”",
      highlighted: false,
      step: 2,
    },
  ],
  rejectionTerminalDialogue:
    "“Alright then, perhaps some other time,” the figure responds, before vanishing entirely. The page is now static, but still links to the FAQ and Terms pages.",
  preLoginAgreement:
    "By clicking “sign up” below [OR “log-in”/”continue” - whichever text will appear on the call to action button], you are agreeing to the LIGHT Supplemental Terms of Service and Meta Platform, Inc.'s Data Policy and you consent for us to use a cookie to track your logged-in status across the LIGHT site. Learn more about how we use cookies here. In order to play LIGHT, you are required to login via your valid Facebook account. You must be at least 18 years of age or older and reside in the United States in order to play.",
  legalAgreements: [
    "1. I am 18 years of age or older (or, if higher than 18, the age of majority in the jurisdiction from which I am accessing LIGHT) and reside in the United States.",
    "2. I understand LIGHT is for research, and LIGHT Agents can make untrue or offensive statements. If this happens, I pledge to report these issues to help improve future research. Furthermore, I agree not to intentionally trigger others to make offensive statements.",
    "3. I understand that interactions in LIGHT are set in a fantasy environment, and content inside is not intended to reflect real-world circumstances.",
    "4. I understand that in-game interactions will be published publicly and used for future research. Therefore, I agree not to mention any personally identifiable information in the content of my conversations, including names, addresses, emails, and phone numbers. [link to additional info on our use of your data in the FAQ’s]",
  ],
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
