
/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* IMAGES */
// CHAT
import ChatBox from "./assets/screenshots/chatbox.png";
import DoChatBar from "./assets/screenshots/dochatbar.png";
import SayChatBar from "./assets/screenshots/saychatbar.png";
import TellChatBar from "./assets/screenshots/tellchatbar.png";
// HUD INFO
import CharacterInfo from "./assets/screenshots/characterinfo.png";
import MissionInfo from "./assets/screenshots/missioninfo.png";
import SettingInfo from "./assets/screenshots/settinginfo.png";
// Reporting flow
import BadMessage from "./assets/screenshots/badmessage.png";
import ClickReport from "./assets/screenshots/clickreport.png";
import ReportModal from "./assets/screenshots/reportmodal.png";



// Copy for Preview Blurb
const PreviewCopy = {
    intro: "In this task you will be playing a text based adventure game.  In this game you will be expected to stay in character and must complete a minimum number of 15 say interactions and 10 do interactions.  These are the absolute minimum, but additional quality turns will be bonused proportionately.  You should attempt your provided goal, but are not required to complete it in the given time.  Once you have completed your session you will be able to submit your session data for evaluatioon and comment on your experience.  Any feedback about your experience is appreciated.",
    uiSteps:[
        {
            image: CharacterInfo,
            text: "This is the persona of your assigned character.  Use this description to help guide you towards dialogue and actions that would best fit the character."
        },
        {
            image: MissionInfo,
            text: "In this section you can see you character's primary goals and motivations.  Look to this when you are uncertain of what you should be trying to accomplish."
        },
        {
            image: SettingInfo,
            text: "In this section you can see your character's immediate surroundings. Here you can see items that you can pick up or directions you can move. These will appear in the chat thread as you move around."
        }
    ],
    chatSteps:[
        {
            image: ChatBox,
            text: "In the chat display you can see the actions and dialogue of your character as well as other characters.  You can enter text at the bottom of the chat display. Characters in the vicinity can be seen on the top of the chat window.  "
        },
        {
            image: SayChatBar,
            text: "You can switch between Say and Do mode by clicking the Say/Do button or pressing the ` key.  Saying something will be heard by every character in the vincinity."
        },
        {
            image: DoChatBar,
            text: "As stated above you can switch to Do mode by clicking the Say Button or pressing the ` key.  In do mode you can interact with the world.  Type help if you wish to view some common commands. You can move from area to area or pick up objects while in Do mode."
        },
        {
            image: TellChatBar,
            text: "Clicking on a character's name up top, or clicking the reply button on any message, will allow you tell them something directly, meaning they know you're addressing them specifically."
        }
    ],
    reportSteps:[
        {
            image: BadMessage,
            text: "Sometimes the game makes a mistake, and says things that are innapropriate or don't make sense."
        },
        {
            image: ClickReport,
            text: "If this occurs, please press the X on the affected message and click the REPORT THIS NOW text."
        },
        {
            image: ReportModal,
            text: "This will bring up a modal, where you can mark what's wrong with the message. Fill this out and describe the issue with any affected messages."
        }
    ]
}


export default PreviewCopy;
