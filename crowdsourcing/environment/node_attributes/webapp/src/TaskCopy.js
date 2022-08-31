/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/*----------------SCREENSHOTS/IMAGES----------------*/
/*SELECTION*/
import Selection from "./assets/images/tutorial/Selection.png";
/*SUBMIT BUTTON*/
import SubmitButton from "./assets/images/tutorial/SubmitButton.png";
/*TOOLTIP*/
import BooleanAttributeTooltip from "./assets/images/tutorial/BooleanAttributeTooltip.png";
/*---------STEP SCREENSHOTS---------*/

/*-------SCALES-------*/
/*ATTRIBUTE SCALE STEPS*/
import AttributeScale1 from "./assets/images/tutorial/AttributeScale/AttributeScale1.png";
import AttributeScale2 from "./assets/images/tutorial/AttributeScale/AttributeScale2.png";
import AttributeScale3 from "./assets/images/tutorial/AttributeScale/AttributeScale3.png";

/*CUSTOM ATTRIBUTE SCALE STEPS*/
import CustomAttributeScale1 from "./assets/images/tutorial/CustomAttributeScale/CustomAttributeScale1.png";
import CustomAttributeScale2 from "./assets/images/tutorial/CustomAttributeScale/CustomAttributeScale2.png";
import CustomAttributeScale3 from "./assets/images/tutorial/CustomAttributeScale/CustomAttributeScale3.png";

/*-------TYPE SPECIFIC-------*/
/*ATTRIBUTE CHECKLIST STEPS*/
import AttributeChecklist1 from "./assets/images/tutorial/AttributeChecklist/AttributeChecklist1.png";
import AttributeChecklist2 from "./assets/images/tutorial/AttributeChecklist/AttributeChecklist2.png";
import AttributeChecklist3 from "./assets/images/tutorial/AttributeChecklist/AttributeChecklist3.png";

/*NUMERIC ATTRIBUTE STEPS*/
import NumericAttribute1 from "./assets/images/tutorial/NumericAttribute/NumericAttribute1.png";
import NumericAttribute2 from "./assets/images/tutorial/NumericAttribute/NumericAttribute2.png";
import NumericAttribute3 from "./assets/images/tutorial/NumericAttribute/NumericAttribute3.png";

/*ATTRIBUTE RADIO STEPS*/
import AttributeRadio1 from "./assets/images/tutorial/AttributeRadio/AttributeRadio1.png";
import AttributeRadio2 from "./assets/images/tutorial/AttributeRadio/AttributeRadio2.png";
import AttributeRadio3 from "./assets/images/tutorial/AttributeRadio/AttributeRadio3.png";

/*-------BOOLEAN-------*/
/*BOOLEAN ATTRIBUTE STEPS*/
import BooleanAttribute1 from "./assets/images/tutorial/BooleanAttribute/BooleanAttribute1.png";
import BooleanAttribute2 from "./assets/images/tutorial/BooleanAttribute/BooleanAttribute2.png";
import BooleanAttribute3 from "./assets/images/tutorial/BooleanAttribute/BooleanAttribute3.png";


const Copy ={
    taskHeader:"Fantasy Object Attribute Annotation",
    previewCopy:{
        tutorial:{
            intro: "In this task you will be given a list of objects, and asked to do a number of annotations of the types listed below. Familiarize yourself with these before getting started.",
            questionsCopy:[
                {
                    questionName: "Rating Scale",
                    steps:[
                        {
                            stepCopy: "The Rating Scale form shows an attribute and description at the top and contains a selection of flags in the box to the left and the range and examples in the container to the right.",
                            stepImg: AttributeScale1
                        },
                        {
                            stepCopy: 'Click and drag a "flag" of the selection you wish to rate.  Once out of the gallery you will notice a "pole" will appear when you release the "flag."  Place the pole where you believe the selection falls on the scale relative to the provided examples and other selection items.',
                            stepImg: AttributeScale2
                        },
                        {
                            stepCopy: 'The form will be completed when all of the flags are planted.',
                            stepImg: AttributeScale3
                        }
                    ]
                },
                {
                    questionName: "Custom Rating Scale",
                    steps:[
                        {
                            stepCopy: "This form is similar to the previous Rating Scale however in this form you will be naming and describing an attribute that applies to all of the selection.  Input the attribute name and description in the fields provided at the top of the form.",
                            stepImg: CustomAttributeScale1
                        },
                        {
                            stepCopy: 'Once you fill in the fields to rate the selection click and drag the "flag" of the selection you wish to rate, once out of the selection gallery box you will notice a "pole" will appear when you release the "flag."  Place the pole where you believe the selection falls on the scale relative to the provided examples and other selection items.',
                            stepImg: CustomAttributeScale2
                        },
                        {
                            stepCopy: 'The form will be completed when all of the flags are planted and when the name and description fields have been filled in.',
                            stepImg: CustomAttributeScale3
                        }
                    ]
                },
                {
                    questionName: "Attribute Checklist",
                    steps:[
                        {
                            stepCopy: "In this form you will be given the selection with a list of attributes and there corresponding checkboxes.",
                            stepImg: AttributeChecklist1
                        },
                        {
                            stepCopy: 'Check the box of each attribute that applies to the selection item next to it.',
                            stepImg: AttributeChecklist2
                        },
                        {
                            stepCopy: 'The form will be completed when you have assigned the relevant attributes to the entire selection.',
                            stepImg: AttributeChecklist3
                        }
                    ]
                },
                {
                    questionName: "Numeric Attributes",
                    steps:[
                        {
                            stepCopy: "For this form you will be provided with the an attribute or attributes that are associated with a specific number.",
                            stepImg: NumericAttribute1
                        },
                        {
                            stepCopy: 'Using what you know about the selection assign a number value to each of these attributes as they relate to their selection item.',
                            stepImg: NumericAttribute2
                        },
                        {
                            stepCopy: 'The form will be completed when you have assigned a number to every attribute for the entire selection.',
                            stepImg: NumericAttribute3
                        }
                    ]
                },
                {
                    questionName: "Attribute Choice",
                    steps:[
                        {
                            stepCopy: "For this form you will be provided with a list of mutually exclusive attributes next to each selection item.",
                            stepImg: AttributeRadio1
                        },
                        {
                            stepCopy: 'Only one of the attributes can be selected at a time so select the attribute that best fits based on your knowledge of the selection.',
                            stepImg: AttributeRadio2
                        },
                        {
                            stepCopy: 'The form will be completed when the entire selection has been given attributes.',
                            stepImg: AttributeRadio3
                        }
                    ]
                },
                {
                    questionName: "Boolean Attributes",
                    steps:[
                        {
                            stepCopy: "For this form you will be either choosing existing attributes from a dropdown or adding your own attributes to the entire selection.",
                            stepImg: BooleanAttribute1
                        },
                        {
                            stepCopy: 'Each input may have some options in a dropdown but you can add your own attributes as well by typing the attribute and clicking add new attribute in the dropdown.',
                            stepImg: BooleanAttribute2
                        },
                        {
                            stepCopy: 'The form is complete when at least 4 attributes have been given to each of the selection.',
                            stepImg: BooleanAttribute3
                        }
                    ]
                },
            ]
        }
    },
    tagQuestionHeader:"ATTRIBUTES",
    attributeQuestionHeader:"ATTRIBUTES",
    successMessage:"You have successfully submitted completed task!",
    objects:{
        defaultQuestions:[
            {
                questionType:"multipleSelect",
                question:"# is:  ",
                options:[
                    {
                        name:"a container.",
                        value: "container"
                    },
                    {
                        name:"a surface.",
                        value: "surface"
                    },
                    {
                        name:"living.",
                        value: "living"
                    },
                    {
                        name:"wieldable.",
                        value: "wieldable"
                    },                    {
                        name:"wearable.",
                        value: "wearable"
                    }
                ]
            }
        ],
        defaultBooleanAttributeOptions:[],
        traits:[
            {
                name: "SIZE",
                description:"The physical size of an object",
                scaleRange:[
                    {
                    name:"MIN",
                    example: "Nail",
                    color:"green"
                    },
                    {
                    name:"MID",
                    example: "Sword",
                    color:"blue"
                    },
                    {
                    name:"MAX",
                    example: "Wagon",
                    color:"red"
                    }
                ]
            },
            {
                name: "VALUE",
                description:"The monetary value of an object.",
                scaleRange:[
                    {
                    name:"MIN",
                    example: "Rock",
                    color:"green"
                    },
                    {
                    name:"MID",
                    example: "Silver Piece",
                    color:"blue"
                    },
                    {
                    name:"MAX",
                    example: "Treasure",
                    color:"red"
                    }
                ]
            },
            {
                name: "CONTAINER SIZE",
                description:"The space available inside container for storage.",
                requiredAttribute:"container",
                scaleRange:[
                    {
                    name:"MIN",
                    example: "A Locket",
                    color:"green"
                    },
                    {
                    name:"MID",
                    example: "Satchel",
                    color:"blue"
                    },
                    {
                    name:"MAX",
                    example: "Shipping Crate",
                    color:"red"
                    }
                ]
            },
            {
                name: "WEAPON DAMAGE",
                description:"The base damage a weapon does when wielded agaisnt a foe.",
                requiredAttribute:"wieldable",
                scaleRange:[
                    {
                    name:"MIN",
                    example: "Stick",
                    color:"green"
                    },
                    {
                    name:"MID",
                    example: "Sword",
                    color:"blue"
                    },
                    {
                    name:"MAX",
                    example: "Ballista",
                    color:"red"
                    }
                ]
            },
            {
                name: "ARMOR RATING",
                description:"The amount of protection a wearable object offers",
                requiredAttribute:"armor",
                scaleRange:[
                    {
                    name:"MIN",
                    example: "Shirt",
                    color:"green"
                    },
                    {
                    name:"MID",
                    example: "Leather Vest",
                    color:"blue"
                    },
                    {
                    name:"MAX",
                    example: "Platemail",
                    color:"red"
                    }
                ]
            },
            {
                name: "REFRESHMENT",
                description:"How refreshing an object is when consumed.",
                requiredAttribute:"consumable",
                scaleRange:[
                    {
                    name:"MIN",
                    example: "Millet",
                    color:"green"
                    },
                    {
                    name:"MID",
                    example: "Bread",
                    color:"blue"
                    },
                    {
                    name:"MAX",
                    example: "A feast",
                    color:"red"
                    }
                ]
            },
            {
                name: "WEIGHT",
                description:"The heaviness of an object.",
                scaleRange:[
                    {
                    name:"MIN",
                    example: "A Feather",
                    color:"green"
                    },
                    {
                    name:"MID",
                    example: "Pile of wood",
                    color:"blue"
                    },
                    {
                    name:"MAX",
                    example: "A Large Boulder",
                    color:"red"
                    }
                ]
            },
            {
                name: "RARITY",
                description:"How common the object is in the world.",
                scaleRange:[
                    {
                    name:"MIN",
                    example: "A rock",
                    color:"green"
                    },
                    {
                    name:"MID",
                    example: "Iron",
                    color:"blue"
                    },
                    {
                    name:"MAX",
                    example: "Excalibur",
                    color:"red"
                    }
                ]
            },
            {
                name: "USEFULNESS",
                description:"How likely is the it that he object will be used?",
                scaleRange:[
                    {
                    name:"MIN",
                    example: "Almost Never",
                    color:"green"
                    },
                    {
                    name:"MID",
                    example: "Fairly Often",
                    color:"blue"
                    },
                    {
                    name:"MAX",
                    example: "Almost Never",
                    color:"red"
                    }
                ]
            },
        ]
        },
    characters:{
        defaultQuestions:[
            {
                question:"# arm count:  ",
                questionType:"numeric",
                field:"arms"
            },
            {
                question:"# leg count:  ",
                questionType:"numeric",
                field:"legs"
            }
        ],
        defaultBooleanAttributeOptions:[],
        traits:[
            {
                name: "STRENGTH",
                description:"The raw physical power an actor can exert typically fort he express purpose of attacking.",
                scaleRange:[
                    {
                    name:"MIN",
                    example: "Rat",
                    color:"green"
                    },
                    {
                    name:"MID",
                    example: "Peasant",
                    color:"blue"
                    },
                    {
                    name:"MAX",
                    example: "Dragon",
                    color:"red"
                    }
                ]
            },
            {
                name: "CONSTITUTION",
                description:"The physical toughness and ability to take damage possessed by an actor",
                scaleRange:[
                    {
                    name:"MIN",
                    example: "Butterfly",
                    color:"green"
                    },
                    {
                    name:"MID",
                    example: "Peasant",
                    color:"blue"
                    },
                    {
                    name:"MAX",
                    example: "Stone Golem",
                    color:"red"
                    }
                ]
            },
            {
                name: "CHARISMA",
                description:"",
                scaleRange:[
                    {
                    name:"MIN",
                    example: "A Gelatinous Cube",
                    color:"green"
                    },
                    {
                    name:"MID",
                    example: "Bard",
                    color:"blue"
                    },
                    {
                    name:"MAX",
                    example: "Dryad",
                    color:"red"
                    }
                ]
            },
            {
                name: "DEXTERITY",
                description:"The speed, skill, and agility of an actor.",
                scaleRange:[
                    {
                    name:"MIN",
                    example: "Living Statue",
                    color:"green"
                    },
                    {
                    name:"MID",
                    example: "Peasant",
                    color:"blue"
                    },
                    {
                    name:"MAX",
                    example: "Legendary Thief",
                    color:"red"
                    }
                ]
            },
            {
                name: "INTELLIGENCE",
                description:"The ability of an actor to learn and retain knowledge both magical and practical.",
                scaleRange:[
                    {
                    name:"MIN",
                    example: "A Stump",
                    color:"green"
                    },
                    {
                    name:"MID",
                    example: "Student",
                    color:"blue"
                    },
                    {
                    name:"MAX",
                    example: "Wizard Prodigy",
                    color:"red"
                    }
                ]
            },
            {
                name: "WISDOM",
                description:"An actor's willpower to make good decisions and experience to know what decisions are good.",
                scaleRange:[
                    {
                    name:"MIN",
                    example: "Wildboar",
                    color:"green"
                    },
                    {
                    name:"MID",
                    example: "Peasant",
                    color:"blue"
                    },
                    {
                    name:"MAX",
                    example: "Ancient Sage",
                    color:"red"
                    }
                ]
            },
            {
                name: "SIZE",
                description:"The physical size of an actor",
                scaleRange:[
                    {
                    name:"MIN",
                    example: "An Ant",
                    color:"green"
                    },
                    {
                    name:"MID",
                    example: "Human",
                    color:"blue"
                    },
                    {
                    name:"MAX",
                    example: "A Giant",
                    color:"red"
                    }
                ]
            },
            {
                name: "RARITY",
                description:"How common the actor is in the world.",
                scaleRange:[
                    {
                    name:"MIN",
                    example: "Peasant",
                    color:"green"
                    },
                    {
                    name:"MID",
                    example: "Knight",
                    color:"blue"
                    },
                    {
                    name:"MAX",
                    example: "Royalty",
                    color:"red"
                    }
                ]
            },
        ]
      },
      locations:{
        defaultQuestions:[
            {
                questionType:"multipleChoice",
                question:"# is:  ",
                options:[
                    {
                        name:"Indoors",
                        value: "indoors"
                    },
                    {
                        name:"Outdoors",
                        value: "outdoors"
                    }
                ]
            }
        ],
        defaultBooleanAttributeOptions:[],
        traits:[
            {
                name: "SIZE",
                description:"The size of a location.",
                scaleRange:[
                    {
                    name:"MIN",
                    example: "Hut",
                    color:"green"
                    },
                    {
                    name:"MID",
                    example: "Field",
                    color:"blue"
                    },
                    {
                    name:"MAX",
                    example: "Castle",
                    color:"red"
                    }
                ]
            },
            {
                name: "BRIGHTNESS",
                description:"The natural light and visibility of a location.",
                scaleRange:[
                    {
                    name:"MIN",
                    example: "Cave",
                    color:"green"
                    },
                    {
                    name:"MID",
                    example: "Candlelit Home",
                    color:"blue"
                    },
                    {
                    name:"MAX",
                    example: "A Field at Noon",
                    color:"red"
                    }
                ]
            },
            {
                name: "TEMPERATURE",
                description:"The room temperature of a location",
                scaleRange:[
                    {
                    name:"MIN",
                    example: "Ice Cave",
                    color:"green"
                    },
                    {
                    name:"MID",
                    example: "Meadow",
                    color:"blue"
                    },
                    {
                    name:"MAX",
                    example: "Lava Cave",
                    color:"red"
                    }
                ]
            },
            {
                name: "RARITY",
                description:"The rarity of a location",
                scaleRange:[
                    {
                    name:"MIN",
                    example: "Field",
                    color:"green"
                    },
                    {
                    name:"MID",
                    example: "Village",
                    color:"blue"
                    },
                    {
                    name:"MAX",
                    example: "Secret Room",
                    color:"red"
                    }
                ]
            },
        ]
      },
      input:{
        defaultBooleanAttributes:[
        ],
        defaultScaleRange:[
            {
            name:"MIN",
            example: "Min",
            color:"green"
            },
            {
            name:"MID",
            example: "Mid",
            color:"blue"
            },
            {
            name:"MAX",
            example: "Max",
            color:"red"
            }
        ]
      },
}

export default Copy;
