const Copy ={
    constraint:{
        questions:[
            "# Constraints for Interaction:  ",
            "1.  Does # need to be held?",
            "2.  Could one use # with # and expect the same outcome?",
            "3.  Would this have to happen in a specific place?",
            "Where would that location be?",
        ]
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
