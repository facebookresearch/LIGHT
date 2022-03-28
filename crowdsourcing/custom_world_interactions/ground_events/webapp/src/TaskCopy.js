//HEADER SCREENSHOT
const HeaderShot = require("./assets/images/Tutorial/HeaderShot.png");
//EVENT SCREENSHOTS
const EventShot1 = require("./assets/images/Tutorial/Event/EventShot1.png");
const EventShot2 = require("./assets/images/Tutorial/Event/EventShot2.png");
const EventShot3 = require("./assets/images/Tutorial/Event/EventShot3.png");
const EventShot4 = require("./assets/images/Tutorial/Event/EventShot4.png");
const EventShot5 = require("./assets/images/Tutorial/Event/EventShot5.png");

const Copy ={
    tutorialIntro:{
        explanation:"We're trying to crowdsource interactions between two objects. These interactions will be set in a medieval fantasy scenario, and as such should not refer to real people, places, or modern day technologies.  The objective of this task is to focus on two aspects of the interaction:  The events that occur during the interaction and the constraints required for the interaction to take place.  At the top of the screen you will be presented with 3 cards, the first two will be the names and a brief description of the objects involved in the interaction, the third contains the narration for the interaction itself.  Reference this information while completing the task.",
        screenshot: HeaderShot
    },
    event:{
        tutorialIntro:"The events section pertains to what changes(if any) occured during the interaction.  You will be tasked with narrating what this interaction looks like to a third party then describing anything that was created, destroyed, or changed as result of the interaction.",
        questions:{
            1: "1.  Narrate this specific interaction to another observer who sees it happen.",
            2: "2.  Are objects removed?",
            a2: "2a.  Which object(s)?",
            3: "3.  Does an object's description change?",
            4: "4.  Are objects created?",
            5: "5.  Do any of the objects change location?",
            a5: "Where does selected object move?",
            setter: " After this action:  "
        },
        tutorialCopy:[
            {
                question:"1)  Narrate this interaction",
                explanation:'The new narration should be directed to someone observing the interaction take place, say in the same location.  If you want to refer to the actor, location, or either the key or the lock, use `ACTOR`, `LOCATION`, `OBJECT1`, `OBJECT2`.  For example, "You place the key in the lock and turn. After a satisfying click the lock becomes unlocked " could be seen as "ACTOR fumbles with a OBJECT1 in the OBJECT2 for a moment, before you hear a click echo through LOCATION."',
                screenshot: EventShot1

            },
            {
                question:"2) Are objects removed?",
                explanation:`If the interaction would cause one of the
                used objects not exist anymore, mark those
                objects.

                For instance, if the interaction was "The lit
                torch ignites the table, and the table burns
                to the ground, leaving a pile of ashes."
                In this case you would mark that an object
                is removed, specifically the table. The torch
                is not removed.`,
                screenshot: EventShot2
            },
            {
                question:"3) Do object descriptions change?",
                explanation:`If an object remains in the scene, but it ends
                up changed by the interaction, it's description
                should change. For instance given "You
                scratch the side of the shiny bucket with
                a rusty key.", the description of the bucket
                may change from "A shiny bucket that must
                have been bought recently" to "A shiny new
                bucket. It would be perfect, if not for the
                deep scratches in one side."`,
                screenshot: EventShot3
            },
            {
                question:"4) Are objects created?",
                explanation:`If the interaction creates new objects in the
                scene, you should list them here. You should
                describe the object and note where the object
                exists. The object can only be created either the
                location the interaction occurs (on the floor), in/on
                one of the other objects (like on a table or in
                a mug), or carried by the actor.

                So, for the example with the torch and
                a wooden table, where the table burns to ashes,
                you may create "Pile of Ash: These ashes are
                fresh and still a little hot." and it would be created
                in the room.`,
                screenshot: EventShot4
            },
            {
            question:"5) Location Changes",
            explanation:`If the described interaction changes the location of an item, use this to mark where the item should be after the interaction`,
            screenshot: EventShot5
            },
        ]
    },
    errorKey:{
        events:{
          q1Blank: "Narration cannot be blank",
          q2Null: "Please click yes or no for object removal event",
          q2Empty:"Please select the item that was removed or click no for this event.",
          q3Null: "Please click yes or no for object description change event",
          q3Blank:"Description cannot be blank",
          q3NoChange:"Both descriptions cannot be the same as before when object description change is selected.",
          q4Null:  "Please click yes or no for object creation event",
          q4MissingField:  "Please click yes or no for object creation event",
          q5Blank: "Please either remove or select a value for selected location change(s)"
        },
        constraint:{
          q1Null:  "Please click yes or no for held constraint",
          q2Null:  "Please click yes or no for reversible constraint",
          q3Null:  "Please click yes or no for times remaining constraint",
          q3Blank:  "Description cannot be blank",
          q4Null:  "Please click yes or no for location constraint",
          q4blank:  "Location cannot be blank please write a location or click no"
        }
      }
}
export default Copy
