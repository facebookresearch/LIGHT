//HEADER SCREENSHOT
const HeaderShot = require("./assets/images/Tutorial/HeaderShot.png");
//EVENT SCREENSHOTS
const Question1 = require("./assets/images/Tutorial/Question1.png");
const Question2 = require("./assets/images/Tutorial/Question2.png");
const Question3 = require("./assets/images/Tutorial/Question3.png");
const Question4 = require("./assets/images/Tutorial/Question4.png");
const Question5 = require("./assets/images/Tutorial/Question5.png");
const Question6 = require("./assets/images/Tutorial/Question6.png");
const Question7 = require("./assets/images/Tutorial/Question7.png");
const Question8 = require("./assets/images/Tutorial/Question8.png");
const Question9 = require("./assets/images/Tutorial/Question9.png");
const Question10 = require("./assets/images/Tutorial/Question10.png");

const Copy = {
    tutorialIntro:{
        explanation: "We're trying to crowdsource interactions between two objects. These interactions will be set in a medieval fantasy scenario, and as such should not refer to real people, places, or modern day technologies.  The objective of this task is to ensure that the given interaction is consistent. At the top of the screen you will be presented with 3 cards, the first two will be the names and a brief description of the objects involved in the interaction, the third contains the narration for the interaction itself.  Reference this information while completing the task.",
        screenshot: HeaderShot
    },
    interaction: {
        tutorialIntro: "The interaction section up at the top presents you with the context of an interaction. Here you'll validate if the interaction makes sense overall, and select which of the objects is the primary object being used (held/operated/moved) by the actor.",
        questions: {
            0: "1. Does this interaction overall make sense? Is the narration of an event where an actor uses these objects together:",
            1: "2. Which item is the actor more likely holding/using to do this interaction:",
        },
        tutorialCopy: [
            {
                question:"1) Does this interaction overall make sense?",
                explanation:'Assess whether the provided interaction makes sense, as in the interaction that occurs is valid when considering the objects and their descriptions.',
                screenshot: Question1
            },
            {
                question:"2) Which item is the actor more likely holding/using to do this interaction?",
                explanation:'Select the item that is the one that the actor is using most in the interaction. Usually, this would be an item the actor can hold or utilize for the interaction. If both need to be held, use "both". If either could be held and used equally, select "either".',
                screenshot: Question2
            },
        ]
    },
    narration: {
        tutorialIntro: "The narration section is used to ensure that narrations of the event are consistent.",
        questions: {
            0: "3. Does this interaction refer to external context? Does it require knowledge about the actor's backstory, or the current location, or make assumptions about what the actor does next?",
            1: "4. Provide a rephrasing of the narration, removing external context if it is present. The outcome should be the same. Replace the narration below (provided for convenience).",
            2: "5. Update the provided narration for a third-party observer, removing context an observer wouldn't know. (Sometimes the narration provided below will refer to external context or details an observer wouldn't know. Remove these if necessary).",
        },
        tutorialCopy: [
            {
                question:"3) Does this interaction refer to external context?",
                explanation:'Assess whether the provided interaction is based entirely on the objects and their descriptions. If the action requires something about the actor\'s backstory, like "ever since you became a knight", or the current location, like "you drop the sword on the forest floor", or about the actor\'s next actions, like "Now you head to the market to sell the ring", or refers to objects not present/created or characters other than the actor, say yes.',
                screenshot: Question3
            },
            {
                question:"4) Provide a rephrasing of the narration, removing external context if it is present.",
                explanation: 'Starting from the given narration, provide a new phrasing of it that captures the same overall outcome. If you marked yes for 3, make sure you omit the additional context in your rephrasing. The rephrasing should remain in second person ("you...").',
                screenshot: Question4
            },
            {
                question:"5) Update the third-person narration of the event, ensuring it remains consistent with the interaction.",
                explanation: 'Update the given third-person narration of the event to ensure it is a reasonable narration for a third party who observes the actor perform the event. Remove any context that an observer wouldn\'t actually know, or update it to be inferred. For instance "{actor} is annoyed" should become "{actor} seems annoyed" as the third party doesn\'t actually know the actor\'s feelings.',
                screenshot: Question5
            },
        ]
    },
    objects: {
        tutorialIntro: "The objects section is used to annotate what objects remain after the interaction, where they are, and what their descriptions may be.",
        questions: {
            0: "6. Ensure the list of objects that remain in the location of the action is consistent with the interaction. Update the list by changing object names or adding and removing objects if it is not. The provided list commonly misses cases where the two objects have been combined into something new.",
            1: "7. Correct the descriptions for the remaining objects to be consistent with the interaction, but clear via observation. The description should be appropriate for a third party observing the object even if they didn't observe the interaction. Avoid time-based descriptions that say things like 'used to be ...' or 'is now', as these aren't known by observation. Try to maintain as much of the original detail as you can.",
            2: "8. Ensure the provided final object locations are correct. Options are 'in/on <another object>', 'in room', 'original location of <original object>', 'held/worn/wielded by actor'",
        },
        tutorialCopy: [
            {
                question:"6) Correct the list of remaining objects.",
                explanation: 'You will be given a list of objects remaining after the interaction. Ensure this list is correct, adding elements to it if necessary. If an object is no longer present (having been combined into something new, destroyed, thrown out of the current location, etc.), remove it from this list. If an object was created in the interaction, but isn\'t present here, add it. For instance, after "You sew the patch onto the shirt", "Patch" should no longer remain but "shirt" will.',
                screenshot: Question6
            },
            {
                question:"7) Correct the remaining object's descriptions",
                explanation: 'Update the provided descriptions to be sure that they\'re both consistent with the interaction (capturing any changes that occur) but only include information that would be clear if one were to look at the object without having seen the interaction. For instance, something like "This pencil was used to write a note" could instead be corrected to "This pencil\'s tip is worn", or removed from the description entirely.',
                screenshot: Question7
            },
            {
                question:"8) Correct the final locations for the objects after the interaction",
                explanation: 'Ensure the provided final object locations are correct. Options are "in/on <another object>", "in room", "original location of <original object>", "held/worn/wielded by actor". If the final location is somewhere far away, the object should instead be removed from the list in question 6.',
                screenshot: Question8
            },
        ]
    },
    attributes: {
        tutorialIntro: "The attributes section is used to determine the properties of an object that are relevant to the interaction. You'll annotate what attributes are required beforehand, whether the interaction changes them, and what attributes should be present after.",
        questions: {
            0: "9. What properties for the objects are required beforehand? Are they removed by the interaction? Provide explanations. Add REMOVED in the reason if the interaction removes this property. For EXTRAS, optionally add a comma-separated list of additional required properties you think are missing, no reason needed. ",
            1: "10. What properties are introduced as a result of the interaction between these objects? For EXTRAS, optionally add a comma-separated list of additional required properties you think are missing, no reason needed.",
        },
        tutorialCopy: [
            {
                question:"9) What properties for the objects are required beforehand? Are they removed?",
                explanation:'You should assess if the provided properties are required by the interaction. For instance, if a blade is being used to cut a rope, it should be "sharp", but it doesn\'t need to be "metal" unless the narration points that out. Your answers should start with "required because" or "not required because". You can extend the list if necessary with comma separated attributes in the "EXTRAS" entry, should there be additional requirements for an object given the narration. If the property is removed by the interaction, add REMOVED to your explanation.',
                screenshot: Question9
            },
            {
                question:"10) What properties for the objects are set by the interaction",
                explanation: 'You should check the provided list of properties and determine whether each was directly caused by the interaction. For instance, if an oak plank is cut in two, then the resultant pieces should be made of oak, so "oak" would be an appropriate property. Or if a sword was wiped, "clean" may be appropriate. Your anwers should start with "required because" or "not required because". These should be consistent with the descriptions in question 7, for instance if a stew is described as "well cooked" then "burnt" would not be an appropriate property. You can extend the list if necessary with comma separated attributes in the "EXTRAS" entry, should there be additional properties for an object given the narration.',
                screenshot: Question10
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
