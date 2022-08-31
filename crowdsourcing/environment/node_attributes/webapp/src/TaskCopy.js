
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
    taskHeader:"Fantasy Entity Attribute Annotation",
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
                            stepCopy: 'Check the box of each attribute that applies to the selection item next to it. The form will be completed when you have assigned the relevant attributes to the entire selection.',
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
    customAttributeQuestionToolTip:'This form is similar to the previous Rating Scale however in this form you will be naming and describing an attribute that applies to all of the selection.  Input the attribute name and description in the fields provided at the top of the form. \n Once you fill in the fields to rate the selection click and drag the "flag" of the selection you wish to rate, once out of the selection gallery box you will notice a "pole" will appear when you release the "flag."  Place the pole where you believe the selection falls on the scale relative to the provided examples and other selection items. \n The form will be completed when all of the flags are planted and when the name and description fields have been filled in.',
    booleanAttributeToolTip:'For this form you will be either choosing existing attributes from a dropdown or adding your own attributes to the entire selection. \n Each input may have some options in a dropdown but you can add your own attributes as well by typing the attribute and clicking add new attribute in the dropdown. \n The form is complete when at least 4 attributes have been given to each of the selection.',
    successMessage:"You have successfully submitted completed task!",
    objects:{
        defaultQuestions:[
            {
                questionType:"multipleSelect",
                question:"# is:  ",
                toolTip: "In this form you will be given the selection with a list of attributes and there corresponding checkboxes. \n Check the box of each attribute that applies to the selection item next to it. The form will be completed when you have assigned the relevant attributes to the entire selection.",
                options:[
                    {
                        name:"a container.",
                        value: "container"
                    },
                    {
                        name:"a surface (to place things on).",
                        value: "surface"
                    },
                    {
                        name:"living (not including plant life).",
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
        defaultBooleanAttributeOptions:[
            'wieldable', 'wearable', 'food', 'drink', 'container', 'surface', 'carryable',
            'wet', 'dark', 'bright', 'hot', 'cold', 'sharp', 'dull', 'hard', 'soft',
            'fluffy', 'moist', 'damp', 'dry', 'delicious', 'glass', 'wooden', 'metallic',
            'colorful', 'distorted', 'odd',
        ],
        traits:[
            {
                name: "SIZE",
                description:"The physical size of an object",
                toolTip:'The Rating Scale form shows an attribute and description at the top and contains a selection of flags in the box to the left and the range and examples in the container to the right. \n Click and drag a "flag" of the selection you wish to rate.  Once out of the gallery you will notice a "pole" will appear when you release the "flag."  Place the pole where you believe the selection falls on the scale relative to the provided examples and other selection items.  \n The form will be completed when all of the flags are planted.',
                scaleRange:[
                    {
                    name:"MIN",
                    example: "Coin",
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
                toolTip:'The Rating Scale form shows an attribute and description at the top and contains a selection of flags in the box to the left and the range and examples in the container to the right. \n Click and drag a "flag" of the selection you wish to rate.  Once out of the gallery you will notice a "pole" will appear when you release the "flag."  Place the pole where you believe the selection falls on the scale relative to the provided examples and other selection items.  \n The form will be completed when all of the flags are planted.',
                scaleRange:[
                    {
                    name:"MIN",
                    example: "Rock",
                    color:"green"
                    },
                    {
                    name:"MID",
                    example: "Pair of boots",
                    color:"blue"
                    },
                    {
                    name:"MAX",
                    example: "Diamonds",
                    color:"red"
                    }
                ]
            },
            {
                name: "CONTAINER SIZE",
                description:"The space available inside a container or on a surface for storage.",
                toolTip:'The Rating Scale form shows an attribute and description at the top and contains a selection of flags in the box to the left and the range and examples in the container to the right. \n Click and drag a "flag" of the selection you wish to rate.  Once out of the gallery you will notice a "pole" will appear when you release the "flag."  Place the pole where you believe the selection falls on the scale relative to the provided examples and other selection items.  \n The form will be completed when all of the flags are planted.',
                requiredAttribute:"container",
                scaleRange:[
                    {
                    name:"MIN",
                    example: "A dish",
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
                toolTip:'The Rating Scale form shows an attribute and description at the top and contains a selection of flags in the box to the left and the range and examples in the container to the right. \n Click and drag a "flag" of the selection you wish to rate.  Once out of the gallery you will notice a "pole" will appear when you release the "flag."  Place the pole where you believe the selection falls on the scale relative to the provided examples and other selection items.  \n The form will be completed when all of the flags are planted.',
                requiredAttribute:"wieldable",
                scaleRange:[
                    {
                    name:"MIN",
                    example: "Flimsy stick",
                    color:"green"
                    },
                    {
                    name:"MID",
                    example: "Dull sword",
                    color:"blue"
                    },
                    {
                    name:"MAX",
                    example: "Flaming battleaxe",
                    color:"red"
                    }
                ]
            },
            {
                name: "ARMOR RATING",
                description:"The amount of protection a wearable object offers",
                toolTip:'The Rating Scale form shows an attribute and description at the top and contains a selection of flags in the box to the left and the range and examples in the container to the right. \n Click and drag a "flag" of the selection you wish to rate.  Once out of the gallery you will notice a "pole" will appear when you release the "flag."  Place the pole where you believe the selection falls on the scale relative to the provided examples and other selection items.  \n The form will be completed when all of the flags are planted.',
                requiredAttribute:"wearable",
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
                toolTip:'The Rating Scale form shows an attribute and description at the top and contains a selection of flags in the box to the left and the range and examples in the container to the right. \n Click and drag a "flag" of the selection you wish to rate.  Once out of the gallery you will notice a "pole" will appear when you release the "flag."  Place the pole where you believe the selection falls on the scale relative to the provided examples and other selection items.  \n The form will be completed when all of the flags are planted.',
                requiredAttribute:"food|drink",
                scaleRange:[
                    {
                    name:"MIN",
                    example: "Moldy Apple",
                    color:"green"
                    },
                    {
                    name:"MID",
                    example: "Bread",
                    color:"blue"
                    },
                    {
                    name:"MAX",
                    example: "A complete meal",
                    color:"red"
                    }
                ]
            },
            {
                name: "WEIGHT",
                description:"The heaviness of an object.",
                toolTip:'The Rating Scale form shows an attribute and description at the top and contains a selection of flags in the box to the left and the range and examples in the container to the right. \n Click and drag a "flag" of the selection you wish to rate.  Once out of the gallery you will notice a "pole" will appear when you release the "flag."  Place the pole where you believe the selection falls on the scale relative to the provided examples and other selection items.  \n The form will be completed when all of the flags are planted.',
                scaleRange:[
                    {
                    name:"MIN",
                    example: "A Feather",
                    color:"green"
                    },
                    {
                    name:"MID",
                    example: "Bowling ball",
                    color:"blue"
                    },
                    {
                    name:"MAX",
                    example: "A 5ft stone statue",
                    color:"red"
                    }
                ]
            },
            {
                name: "RARITY",
                description:"How common the object might be in the world.",
                toolTip:'The Rating Scale form shows an attribute and description at the top and contains a selection of flags in the box to the left and the range and examples in the container to the right. \n Click and drag a "flag" of the selection you wish to rate.  Once out of the gallery you will notice a "pole" will appear when you release the "flag."  Place the pole where you believe the selection falls on the scale relative to the provided examples and other selection items.  \n The form will be completed when all of the flags are planted.',
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
                description:"How likely would someone be able to make use of this item?",
                toolTip:'The Rating Scale form shows an attribute and description at the top and contains a selection of flags in the box to the left and the range and examples in the container to the right. \n Click and drag a "flag" of the selection you wish to rate.  Once out of the gallery you will notice a "pole" will appear when you release the "flag."  Place the pole where you believe the selection falls on the scale relative to the provided examples and other selection items.  \n The form will be completed when all of the flags are planted.',
                scaleRange:[
                    {
                    name:"MIN",
                    example: "pebble",
                    color:"green"
                    },
                    {
                    name:"MID",
                    example: "torch",
                    color:"blue"
                    },
                    {
                    name:"MAX",
                    example: "toolbox",
                    color:"red"
                    }
                ]
            },
        ]
        },
    characters:{
        defaultQuestions:[
            // {
            //     question:"# arm count:  ",
            //     questionType:"numeric",
            //     toolTip:"For this form you will be provided with the an attribute or attributes that are associated with a specific number. \n Using what you know about the selection assign a number value to each of these attributes as they relate to their selection item. \n The form will be completed when you have assigned a number to every attribute for the entire selection.",
            //     field:"arms"
            // },
            // {
            //     question:"# leg count:  ",
            //     toolTip:"For this form you will be provided with the an attribute or attributes that are associated with a specific number. \n Using what you know about the selection assign a number value to each of these attributes as they relate to their selection item. \n The form will be completed when you have assigned a number to every attribute for the entire selection.",
            //     questionType:"numeric",
            //     field:"legs"
            // }
        ],
        defaultBooleanAttributeOptions:[],
        traits:[
            {
                name: "STRENGTH",
                description:"The raw physical power an actor can exert typically for the express purpose of attacking.",
                toolTip:'The Rating Scale form shows an attribute and description at the top and contains a selection of flags in the box to the left and the range and examples in the container to the right. \n Click and drag a "flag" of the selection you wish to rate.  Once out of the gallery you will notice a "pole" will appear when you release the "flag."  Place the pole where you believe the selection falls on the scale relative to the provided examples and other selection items.  \n The form will be completed when all of the flags are planted.',
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
                toolTip:'The Rating Scale form shows an attribute and description at the top and contains a selection of flags in the box to the left and the range and examples in the container to the right. \n Click and drag a "flag" of the selection you wish to rate.  Once out of the gallery you will notice a "pole" will appear when you release the "flag."  Place the pole where you believe the selection falls on the scale relative to the provided examples and other selection items.  \n The form will be completed when all of the flags are planted.',
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
                description:"The ability of an actor to befriend and persuade people.",
                toolTip:'The Rating Scale form shows an attribute and description at the top and contains a selection of flags in the box to the left and the range and examples in the container to the right. \n Click and drag a "flag" of the selection you wish to rate.  Once out of the gallery you will notice a "pole" will appear when you release the "flag."  Place the pole where you believe the selection falls on the scale relative to the provided examples and other selection items.  \n The form will be completed when all of the flags are planted.',
                scaleRange:[
                    {
                    name:"MIN",
                    example: "A Gelatinous Cube",
                    color:"green"
                    },
                    {
                    name:"MID",
                    example: "Barkeep",
                    color:"blue"
                    },
                    {
                    name:"MAX",
                    example: "Cult Leader",
                    color:"red"
                    }
                ]
            },
            {
                name: "DEXTERITY",
                description:"The speed, skill, and agility of an actor.",
                toolTip:'The Rating Scale form shows an attribute and description at the top and contains a selection of flags in the box to the left and the range and examples in the container to the right. \n Click and drag a "flag" of the selection you wish to rate.  Once out of the gallery you will notice a "pole" will appear when you release the "flag."  Place the pole where you believe the selection falls on the scale relative to the provided examples and other selection items.  \n The form will be completed when all of the flags are planted.',
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
                toolTip:'The Rating Scale form shows an attribute and description at the top and contains a selection of flags in the box to the left and the range and examples in the container to the right. \n Click and drag a "flag" of the selection you wish to rate.  Once out of the gallery you will notice a "pole" will appear when you release the "flag."  Place the pole where you believe the selection falls on the scale relative to the provided examples and other selection items.  \n The form will be completed when all of the flags are planted.',
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
                toolTip:'The Rating Scale form shows an attribute and description at the top and contains a selection of flags in the box to the left and the range and examples in the container to the right. \n Click and drag a "flag" of the selection you wish to rate.  Once out of the gallery you will notice a "pole" will appear when you release the "flag."  Place the pole where you believe the selection falls on the scale relative to the provided examples and other selection items.  \n The form will be completed when all of the flags are planted.',
                scaleRange:[
                    {
                    name:"MIN",
                    example: "Wild boar",
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
                toolTip:'The Rating Scale form shows an attribute and description at the top and contains a selection of flags in the box to the left and the range and examples in the container to the right. \n Click and drag a "flag" of the selection you wish to rate.  Once out of the gallery you will notice a "pole" will appear when you release the "flag."  Place the pole where you believe the selection falls on the scale relative to the provided examples and other selection items.  \n The form will be completed when all of the flags are planted.',
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
                description:"How rare it would be to find this actor in a fantasy world.",
                toolTip:'The Rating Scale form shows an attribute and description at the top and contains a selection of flags in the box to the left and the range and examples in the container to the right. \n Click and drag a "flag" of the selection you wish to rate.  Once out of the gallery you will notice a "pole" will appear when you release the "flag."  Place the pole where you believe the selection falls on the scale relative to the provided examples and other selection items.  \n The form will be completed when all of the flags are planted.',
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
                toolTip: "For this form you will be provided with a list of mutually exclusive attributes next to each selection item. \n Only one of the attributes can be selected at a time so select the attribute that best fits based on your knowledge of the selection. \n The form will be completed when the entire selection has been given attributes.",
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
                toolTip:'The Rating Scale form shows an attribute and description at the top and contains a selection of flags in the box to the left and the range and examples in the container to the right. \n Click and drag a "flag" of the selection you wish to rate.  Once out of the gallery you will notice a "pole" will appear when you release the "flag."  Place the pole where you believe the selection falls on the scale relative to the provided examples and other selection items.  \n The form will be completed when all of the flags are planted.',
                scaleRange:[
                    {
                    name:"MIN",
                    example: "Closet",
                    color:"green"
                    },
                    {
                    name:"MID",
                    example: "Swimming pool",
                    color:"blue"
                    },
                    {
                    name:"MAX",
                    example: "Field",
                    color:"red"
                    }
                ]
            },
            {
                name: "BRIGHTNESS",
                description:"The natural light and visibility of a location.",
                toolTip:'The Rating Scale form shows an attribute and description at the top and contains a selection of flags in the box to the left and the range and examples in the container to the right. \n Click and drag a "flag" of the selection you wish to rate.  Once out of the gallery you will notice a "pole" will appear when you release the "flag."  Place the pole where you believe the selection falls on the scale relative to the provided examples and other selection items.  \n The form will be completed when all of the flags are planted.',
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
                description:"The expected temperature of a location",
                toolTip:'The Rating Scale form shows an attribute and description at the top and contains a selection of flags in the box to the left and the range and examples in the container to the right. \n Click and drag a "flag" of the selection you wish to rate.  Once out of the gallery you will notice a "pole" will appear when you release the "flag."  Place the pole where you believe the selection falls on the scale relative to the provided examples and other selection items.  \n The form will be completed when all of the flags are planted.',
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
                description:"The unlikelihood of stumbling into this space in a fantasy world.",
                toolTip:'The Rating Scale form shows an attribute and description at the top and contains a selection of flags in the box to the left and the range and examples in the container to the right. \n Click and drag a "flag" of the selection you wish to rate.  Once out of the gallery you will notice a "pole" will appear when you release the "flag."  Place the pole where you believe the selection falls on the scale relative to the provided examples and other selection items.  \n The form will be completed when all of the flags are planted.',
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
                    example: "Archwizard's Lab",
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
