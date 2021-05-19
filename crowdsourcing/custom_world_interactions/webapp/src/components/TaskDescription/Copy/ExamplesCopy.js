const GoodExamples = [
    {
        primary:"Rusty key",
        secondary:"Bucket",
        narration:"You scrape the key on the edge of the bucket. It sounds terrible, and leaves a mark"
    },
    {
        primary:"Towel",
        secondary:"Rock",
        narration:"You rub the rock with the towel. The rock is now shiny, but the towel could use a cleaning."
    },
    {
        primary:"Rock",
        secondary:"Tree",
        narration:"You throw the rock at the tree. It hits a branch, and a bird flies away."
    }
]

const BadExamples =[
    {
        primary:"shirt",
        secondary:"bucket",
        narration:"You put the shirt in the bucket and it transforms into a pair of pants.",
        badReason: "This interaction isn't very plausible.  Interactions don't need to be expected or mundane, but they should be a realistic occurrence."
    },
    {
        primary:"Ball",
        secondary:"Table",
        narration:"The ball rolls off of the table and falls on the floor.",
        badReason: `This interaction isn't written in second person. The correct format would be "You roll the ball on the table. It falls off of the other side onto the floor"`
    },
    {
        primary:"Tea",
        secondary:"Table",
        narration:"You put the tea on the table but it falls off, leaving a mark on the rug.",
        badReason:"This interaction uses a third object (Rug). It's preferable for the interaction to be generic for any environment, therefore not envolving more than the two objects mentioned."
    },
    {
        primary:"Magical Ring",
        secondary:"Magician",
        narration:"You call a magician with your cellphone and he shows up to analyze the Magical Ring.",
        badReason:"Again, this interaction uses a random third object (Cellphone). It also uses an object which should not exist in the medieval fantasy setting (Cellphone)."
    }
]

export {GoodExamples, BadExamples}
