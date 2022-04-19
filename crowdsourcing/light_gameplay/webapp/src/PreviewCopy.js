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


// Copy for Preview Blurb
const PreviewCopy = {
    intro: "In this task you will be playing a text based adventure game.  In this game you will be expected to stay in character and must complete a minimum number of 15 say interactions and 15 do interactions.  These are the absolute minimum, but additional quality interactions will be bonused proportionately.  Once you have completed your session you will be able to submit your session data for evaluatioon and comment on your experience.  Any feedback about your experience is appreciated.",
    uiSteps:[
        {
            image: CharacterInfo,
            text: "This is the persona of your assigned character.  Use this description to help guide you towards dialogue and actions that would best fit the character."
        },
        {
            image: MissionInfo,
            text: "In this section you can see you character's primary goals and motivations.  Look to this when you are uncertain of what todo."
        },
        {
            image: SettingInfo,
            text: "In this section you can see your character's immediate surroundings.  Here you can see items that you can pick up or directions you can move."
        }
    ],
    chatSteps:[
        {
            image: ChatBox,
            text: "In the chat display you can see the actions and dialogue of your character as well as other characters.  You can enter text at the bottom of the chat display."
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
            text: "Characters in the vicinity can be seen on the bottom of the chat bar.  Clicking on a character's name will allow you tell them something directly, meaning they know you're addressing them specifically."
        }
    ]
}


export default PreviewCopy;
