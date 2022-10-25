import React from "react";

const LandingAppCopy = {
  terminalTypingSpeed: 7,
  terminalDialogue: [
    {
      text:
        "After arriving on this page, you find yourself transported to a new world… ",
      highlighted: false,
      step: 0,
    },
    {
      text: "Look around",
      highlighted: true,
      step: 1,
    },
    {
      text:
        "You can’t really make out much of anything near you. It’s almost as if it’s all a blur, or like you’re suspended underwater. One spot of clarity in the noise: a figure in a cloak gestures in your direction.",
      highlighted: false,
      step: 2,
    },
    {
      text: "“Hello…?”",
      highlighted: true,
      step: 3,
    },
    {
      text:
        "“Welcome to LIGHT, my friend,” it says. “Beyond here is a world of strange characters, interesting locations, and goals to achieve, all serving to help out with AI research on conversational language understanding. Are you interested in participating?”",
      highlighted: false,
      step: 4,
    },
  ],
  rejectionTerminalDialogue:
    "“Alright then, perhaps some other time,” the figure responds, before vanishing entirely.",
  preLoginAgreement:
    "By clicking “log in with Facebook” below, you are agreeing to the LIGHT Supplemental Terms of Service and Meta Platform, Inc.'s Data Policy and you consent for us to use a cookie to track your logged-in status across the LIGHT site. Learn more about how we use cookies here. In order to play LIGHT, you are required to login via your valid Facebook account. You must be at least 18 years of age or older and reside in the United States in order to play.",
  legalAgreements: [
    "1. I am 18 years of age or older (or, if higher than 18, the age of majority in the jurisdiction from which I am accessing LIGHT) and reside in the United States.",
    "2. I understand LIGHT is for research, and LIGHT Agents can make untrue or offensive statements. If this happens, I pledge to report these issues to help improve future research. Furthermore, I agree not to intentionally trigger others to make offensive statements.",
    "3. I understand that interactions in LIGHT are set in a fantasy environment, and content inside is not intended to reflect real-world circumstances.",
    <>
      {"4. I understand that in-game interactions will be "}
      <a
        className="text-blue-500 cursor-pointer underline hover:text-green-100 "
        href="/faq#meta-data-access"
      >
        {"published publicly and used for future research."}
      </a>
      {
        " Therefore, I agree not to mention any personally identifiable information in the content of my conversations, including names, addresses, emails, and phone numbers."
      }
    </>,
  ],
  introDialogueSteps: [
    {
      action: "say",
      actor: "Mysterious Figure",
      text: "Let's get you oriented first",
      isSelf: false,
    },
    {
      action: "say",
      actor: "Mysterious Figure",
      text: "Try saying hello using the chat bar.",
      isSelf: false,
    },
    {
      action: "say",
      actor: "Mysterious Figure",
      text:
        "Well done! Can you do something too? Toggle between saying and doing using the chat button or pressing the ` key.  Try doing something.",
      isSelf: false,
    },
    {
      action: "say",
      actor: "Mysterious Figure",
      text:
        "Great! Also important to the work here is that you can rate messages.  Try clicking on a rating.",
      isSelf: false,
    },
    {
      action: "say",
      actor: "Mysterious Figure",
      text:
        "Seems you know the basics now. With that, have some of this to clear your head.",
      isSelf: false,
    },
    {
      action: "do",
      actor: "Mysterious Figure",
      text:
        "The mysterious figure gives you a mysterious beverage. You drink it. The world begins to clear up a little bit.",
      isSelf: false,
    },
  ],
  termsAndConditions: {
    bullets: [
      `LIGHT groups both artificial intelligence generated chatbot agents ("Agents") and other human players (“Players”) into a shared space, without differentiating between them to the Players. As part of your use of LIGHT, and subject to your compliance with the terms of these Supplemental Terms and the Terms of Service, Meta grants you a limited, non-exclusive, non-sublicensable, non-transferable right to access and use LIGHT. As part of your use of LIGHT, you may make text-based submissions ("Input") to LIGHT. Submitting Input to LIGHT will make it immediately visible for other Agents and Players in-game to view and respond to at will. You may also submit feedback, including but not limited to flagging or reporting other messages for quality or integrity-based issues (altogether, “Feedback”).  Model-generated responses from Agents (“Output”) will be shown when they choose to respond. LIGHT is currently designed for English-only Input and Output. All conversation text contributed to LIGHT (both your and other Players’ Input and Agent’s Output) will be made available on a public website or other platform that can be accessed and used by Meta and others for research purposes.`,
      ``,
      ``,
    ],
  },
};
export default LandingAppCopy;
