const GoodExamples = [
    {
        primary:"Rusty key",
        secondary:"Bucket",
        primary_desc:"This rusty key is incredibly worn. Ow - it's pretty sharp too.",
        secondary_desc:"A pristine looking bucket, without a mark. Must have been made recently.",
        narration:"You scrape the key on the edge of the bucket. It sounds terrible, and leaves a mark"
    },
    {
        primary:"Towel",
        secondary:"Rock",
        primary_desc:"A nice, dry towel. You can't help but like the fabric of it.",
        secondary_desc:"A grimy rock someone got from a swamp. It might be nicer cleaned.",
        narration:"You rub the rock with the towel. The rock is now shiny, but the towel could use a cleaning."
    },
    {
        primary:"Rock",
        secondary:"Tree",
        primary_desc:"A hefty rock. It's hard and heavy.",
        secondary_desc:"This tree has more branches in it than you can count. It has no leaves though.",
        narration:"You throw the rock at the tree. It hits a branch, and a stick falls to the ground."
    },
    {
        primary:"Cutting board",
        secondary:"Benches",
        primary_desc:"A perfect surface for slicing and dicing.",
        secondary_desc:"These benches are stable and great for sitting.",
        narration:"You use the cutting board with the benches to create a workbench. It stays steady and allows you to cut safely."
    },
    {
        primary:"Coarse work clothes",
        secondary:"Large wooden door",
        primary_desc:"These clothes feel rough to the touch, and wouldn't be fun to wear...",
        secondary_desc:"The door is ornate and made of fine wood. A chilly draft is coming in from beneath this door.",
        narration:"You jam the coarse work clothes into the space beneath the large wooden door. The draft subsides."
    }
]

const BadExamples =[
    {
        primary:"shirt",
        secondary:"bucket",
        primary_desc:"A perfecty normal shirt, from a local market.",
        secondary_desc:"A pristine looking bucket, without a mark. Must have been made recently.",
        narration:"You put the shirt in the bucket and it transforms into a pair of pants.",
        badReason: "This interaction isn't very plausible.  Interactions don't need to be expected or mundane, but they should be a realistic occurrence."
    },
    {
        primary:"Ball",
        secondary:"Table",
        primary_desc:"A really round ball. It would roll on any uneven surface.",
        secondary_desc:"This table is of uncertain quality.",
        narration:"The ball rolls off of the table and falls on the floor.",
        badReason: `This interaction isn't written in second person. The correct format would be "You roll the ball on the table. It falls off of the other side onto the floor"`
    },
    {
        primary:"Tea",
        secondary:"Table",
        primary_desc:"Tea in an unassuming mug. It's still warm.",
        secondary_desc:"This table is of uncertain quality.",
        narration:"You put the tea on the table but it falls off, leaving a mark on the rug.",
        badReason:"This interaction uses a third object (Rug). It's preferable for the interaction to be generic for any environment, therefore not envolving more than the two objects mentioned."
    },
    {
        primary:"Magical Ring",
        secondary:"Magician",
        primary_desc:"This ring is arcane and magical in some way. You can't decipher it though.",
        secondary_desc:"A true master of magic. This magician knows what they're talking about.",
        narration:"You call a magician with your cellphone and he shows up to analyze the Magical Ring.",
        badReason:"Again, this interaction uses a random third object (Cellphone). It also uses an object which should not exist in the medieval fantasy setting (Cellphone)."
    },
    {
        primary:"Bed",
        secondary:"Torn pants",
        primary_desc:"This bed has been slept in recently.",
        secondary_desc:"There are more holes than you can count in these pants. You wonder if they're salvagable.",
        narration:"You sit down on the bed to repair your torn pants.",
        badReason:"This interaction isn't between the two objects - the pants don't interact directly with the bed in any way."
    }
]

export {GoodExamples, BadExamples}
