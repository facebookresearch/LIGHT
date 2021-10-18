const DummyWorlds = [
    {
        id:1111, 
        name: "Mars", 
        tags:["#red", "#haunted", "#dry"]
    },
    {
        id:2222, 
        name: "Norrath", 
        tags:["#magical", "#amazing", "#dragons"],
        rooms: [
            {
                id:0, 
                name: "Dungeon", 
                description:"A dark, cold prison.",
                objects: [
                    {id:0, name: "A bone club", description:"A crude weapon made from a large bone."},
                    {id:1, name: "A plate helmet", description:"A shiny piece of armor for one's head."},
                    {id:2, name: "A bucket", description:"An empty vessel that could be used to carry any number of things."}
                  ]
            }
        ]
    }, 
    {
        id:3333, 
        name:"Asgard", 
        tags:["#vikings", "#gods", "#magic"]
    }
]