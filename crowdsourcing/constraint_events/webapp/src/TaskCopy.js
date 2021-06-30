//HEADER SCREENSHOT
const HeaderShot = require("./assets/images/Tutorial/HeaderShot.png");
//EVENT SCREENSHOTS
const EventShot1 = require("./assets/images/Tutorial/Event/EventShot1.png");
const EventShot2 = require("./assets/images/Tutorial/Event/EventShot2.png");
const EventShot3 = require("./assets/images/Tutorial/Event/EventShot3.png");
const EventShot4 = require("./assets/images/Tutorial/Event/EventShot4.png");
const EventShot5 = require("./assets/images/Tutorial/Event/EventShot5.png");


//CONSTRAINT SCREENSHOTS
const ConstraintShot1 = require("./assets/images/Tutorial/Constraint/ConstraintShot1.png");
const ConstraintShot2 = require("./assets/images/Tutorial/Constraint/ConstraintShot2.png");
const ConstraintShot3 = require("./assets/images/Tutorial/Constraint/ConstraintShot3.png");
//const ConstraintShot4 = require("./assets/images/Tutorial/Constraint/ConstraintShot4.png");
const ConstraintShot5 = require("./assets/images/Tutorial/Constraint/ConstraintShot5.png");


const Copy ={
    tutorialIntro:{
        explanation:"We're trying to crowdsource interactions between two objects. These interactions will be set in a medieval fantasy scenario, and as such should not refer to real people, places, or modern day technologies.  The objective of this task is to focus on two aspects of the interaction:  The events that occur during the interaction and the constraints required for the interaction to take place.  At the top of the screen you will be presented with 3 cards, the first two will be the names and a brief description of the objects involved in the interaction, the third contains the narration for the interaction itself.  Reference this information while completing the task.",
        screenshot: HeaderShot
    },
    constraint:{
        tutorialIntro:"The Constraints section focuses on what conditions must be met in order for this interaction to occur.  So for this portion you will be thinking in terms of what must be true for the interaction to have happened in the first place based on the narration.",
        questions:[
            " Constraints for Interaction:  ",
            "1.  Does # need to be held?",
            "2.  Could one use # with # and expect the same outcome?",
            "3.  Can this operation be done an infinite number of times?",
            "3a. How many more times can it be done?",
            "4.  Would this have to happen in a specific place?",
            "4a.  Where would that location be?",
        ],
        tutorialCopy:[
            {
                question:"1) Attributes",
                explanation:`If the interaction requires that the object have
                certain attributes or conditions, they should be listed.

                For instance, if the interaction is "You use the torch
                to ignite the pile of logs on the floor. It catches
                quickly and begins to burn." then you can add the
                constraint that the logs must not be wet.

                Use common sense understanding to determine
                constraints that are relevant for your example.`,
                screenshot: ConstraintShot1
            },
            {
                question:"2) Does object2 need to be held?",
                explanation:`We generally assume that the actor is already holding the first item in the interaction. If the interaction requires the actor to be holding both objects (like if the actor is combining objects), you should mark it here.  For example, for the interaction "You put the gem into the key, then turn it over in your hands. It it's a perfect fit." you would say both objects need to be held.  In contrast for the interaction "You swing the axe at the tree and it rebounds back. Not a mark, this tree must be magic." You would answer that the tree does not need to be held.`,
                screenshot: ConstraintShot2
            },
            {
                question:"3) Can this operation be done an infinite number of times?",
                explanation:`Some interactions are limited in the number of uses. Here
                you should estimate the number of times the interaction
                could be repeated. For instance, for the interaction: "You
                give a piece of the pie to the fox. It eats it quickly and scurries
                back away from you." This kind of interaction must have some
                kind of limit, as your pie has a constant amount. As such you
                may say this interaction could be done 12 times. While we
                don't expect an exact number on this, an estimation will be fine.

                In contrast "You swing the stick at the bucket and it rings out
                loudly, likely annoying anyone in earshot" is an interaction
                that could probably be done indefinitely.`
            },
            {
                question:"4) Could one use Y with X and expect the same outcome?",
                explanation:`Some interactions could be considered to have a direction, for
                instance "using an axe with a tree" is different from "using a
                tree with an axe", though the second here doesn't even make
                sense. However, an interaction like "you mix the milk and the
                flour to start creating some dough" could work with either
                "use milk with flour" or "use flour with milk".

                For unidirectional cases like the former, this would be false.
                For bidirectional cases like the latter, it would be true.`,
                screenshot: ConstraintShot3
            },
            {
                question:"5) Does this interaction need to have in a specific place?",
                explanation:`If the interaction description implies that the interaction
                occurs somewhere specifically, provide a name for the place
                you believe it is happening.

                If it doesn't have any specification, then leave blank.

                For instance the interaction "You mix the the flour and milk
                together to start creating some dough." could happen anywhere,
                so you should say no for an interaction like this.

                However, for something like "You throw the spear at the dragon
                and it recoils, spraying fire breath into the forest around you" then
                this interaction must occur in the forest as it is implied by the
                narration.`,
                screenshot: ConstraintShot5
            }
        ]
    },
    event:{
        tutorialIntro:"The events section pertains to what changes(if any) occured during the interaction.  You will be tasked with narrating what this interaction looks like to a third party then describing anything that was created, destroyed, or changed as result of the interaction.",
        questions:{
            1: "1.  Narrate this interaction to another observer who sees it happen.",
            2: "2.  Are objects removed?",
            a2: "2a.  Which object(s)?",
            3: "3.  Does an object's description change?",
            4: "4.  Are objects created?",
            setter: " After this action:  "
        },
        tutorialCopy:[
            {
                question:"1)  Narrate this interaction",
                explanation:'The new narration should be directed to someone observing the interaction take place, say in the same location.  If you want to refer to the actor, location, or either the key or the lock, use `ACTOR`, `LOCATION`, `KEY`, `LOCK`.For example, "You place the key in the lock and turn. After a satisfying click the lock becomes unlocked " could be seen as "ACTOR fumbles with a KEY in the LOCK for a moment, before you hear a click echo through LOCATION."',
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
                question:"5) Attribute changes",
                explanation:`If the interaction changes something physical
                about an object, you should mark the attribute
                changes here. For instance, if an interaction is
                "You dip the towel in the bucket of oil. It seeps
                into the fabric completely", you may add the
                attributes "wet" and "flammable". This is because,
                after the interaction, the towel must be wet and
                flammable.

                You can also mark that, after the interaction, some
                attributes must not be true. For instance, after the
                above interaction, you could mark that the towel
                will not be "clean" afterwards.`,
                screenshot: EventShot5
            }
        ]
    }
}
export default Copy
