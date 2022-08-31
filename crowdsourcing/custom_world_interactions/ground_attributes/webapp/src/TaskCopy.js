/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

//HEADER SCREENSHOT
const HeaderShot = require("./assets/images/Tutorial/HeaderShot.png");
//EVENT SCREENSHOTS
const EventShot1 = require("./assets/images/Tutorial/Event/EventShot1.png");
const EventShot2 = require("./assets/images/Tutorial/Event/EventShot2.png");
const EventShot3 = require("./assets/images/Tutorial/Event/EventShot3.png");
const EventShot4 = require("./assets/images/Tutorial/Event/EventShot4.png");
const EventShot5 = require("./assets/images/Tutorial/Event/EventShot5.png");
const EventShot6 = require("./assets/images/Tutorial/Event/EventShot6.png");


//CONSTRAINT SCREENSHOTS
const ConstraintShot1 = require("./assets/images/Tutorial/Constraint/ConstraintShot1.png");
const ConstraintShot2 = require("./assets/images/Tutorial/Constraint/ConstraintShot2.png");


const Copy ={
    tutorialIntro:{
        explanation:"We're trying to crowdsource interactions between two objects. These interactions will be set in a medieval fantasy scenario, and as such should not refer to real people, places, or modern day technologies.  The objective of this task is to focus on two aspects of the interaction:  The events that occur during the interaction and the constraints required for the interaction to take place.  At the top of the screen you will be presented with 3 cards, the first two will be the names and a brief description of the objects involved in the interaction, the third contains the narration for the interaction itself.  Reference this information while completing the task.",
        screenshot: HeaderShot
    },
    constraint:{
        tutorialIntro:"The Constraints section focuses on what conditions must be met in order for this interaction to occur.  So for this portion you will be thinking in terms of what must be true for the interaction to have happened in the first place based on the narration.",
        questions:[
            " Constraints for Interaction:  ",
            "1. Is there backstory that can't be represented in constraints?",
            "2.  Does # need to be held?",
            "3.  Could one use # with # and expect the same outcome?",
            "4.  Can this operation be done an infinite number of times?",
            "4a. How many more times can it be done?",
            "5.  Would this have to happen in a specific place?",
            "5a.  Where would that location be?",
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
                question:"2) Backstory",
                explanation:`Some narrations rely on backstory that cannot be created through object constraints.

                For instance, the interaction is "You slowly clean the shield with the cloth,
                thinking about all the fun times you had with your brother", includes backstory (i.e. the brother)
                that is not an inherent attribute of the objects. As a result such an example would be marked true.`,
                screenshot: ConstraintShot2
            },
        ]
    },
    event:{
        tutorialIntro:"The events section pertains to what changes(if any) occured during the interaction.  You will be tasked with narrating what this interaction looks like to a third party then describing anything that was created, destroyed, or changed as result of the interaction.",
        questions:{
            1: "1.  Narrate this interaction to another observer who sees it happen.",
            2: "2.  Are objects removed?",
            t2: "2.  Objects are removed",
            f2: "2.  No objects are removed",
            a2: "2a.  Which object(s)?",
            3: "3.  Does an object's description change?",
            t3: "3.  An object's description changes",
            f3: "3.  No object descriptions change",
            4: "4.  Are objects created?",
            t4: "4.  Objects are created",
            f4: "4.  No objects are created",
            // 5: "5.  Do any of the objects change location?",
            5: "5.  The following objects change location",
            // t5: "5.  Objects change location",
            // f5: "5.  No objects change location",
            a5: "Where does selected object move?",
            6: "Narration the interaction without any story-based backstory.",
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
            {
                question:"6) Attribute changes",
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
                screenshot: EventShot6
            },
            {
                question:"7) Remove Backstory",
                explanation:`If the provided narration contains
                extra backstory (e.g. a reference to a character's past),
                rewrite the narration to remove it. For example, the
                narration "ACTOR hits the OBJECT1 into the OBJECT2, remembering
                how father used to do it before their demise." should
                become "ACTOR hits the OBJECT1 into the OBJECT2.".`,
                // screenshot: EventShot7
                screenshot: null
            }
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
