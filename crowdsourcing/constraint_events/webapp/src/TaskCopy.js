const Copy ={
    constraint:{
        questions:[
            "# Constraints for Interaction:  ",
            "1.  Does # need to be held?",
            "2.  Could one use # with # and expect the same outcome?",
            "3.  Would this have to happen in a specific place?",
            "Where would that location be?",
        ],
        tutorialCopy:{
            1:{
                question:"Narrate this interaction",
                explaination:'The new narration should be directed to someone observing the interaction take place, say in the same location.  If you want to refer to the actor, location, or either the key or the lock, use `ACTOR`, `LOCATION`, `KEY`, `LOCK`.For example, "You place the key in the lock and turn. After a satisfying click the lock becomes unlocked " could be seen as "ACTOR fumbles with a KEY in the LOCK for a moment, before you hear a click echo through LOCATION."'
            }
        }
    },
    event:{
        questions:{
            1: "1.  Narrate this interaction to another observer who sees it happen.",
            2: "2.  Are objects removed?",
            a2: "2a.  Which object(s)?",
            3: "3.  Does an object's description change?",
            4: "4.  Are objects created?",
            setter: "# After this action:  "
        }
    }
}
export default Copy
