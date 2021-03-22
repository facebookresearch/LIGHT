import React, {useState} from "react";
import {Link} from "react-router-dom"
import "react-tippy/dist/tippy.css";
import "emoji-mart/css/emoji-mart.css";



import Scribe from "../../assets/images/scribe.png";
import "../../styles.css";


const LandingPage2 = (props)=>{
    let [page, setPage] = useState(0);
    const [showInstructions, setShowInstructions] = useState(false)
    
    const openInstructions = ()=>{
        setShowInstructions(true)
    }

    const closeInstructions = ()=>{
        setShowInstructions(false)
    }

    const pageChangeHandler = (arrow) =>{
        console.log(page)
        if(page > 0 && arrow === "-"){
            let previousPage = page -=1
            setPage(previousPage)
        }else if(page < 2 && arrow === "+"){
            let nextPage = page +=1
            setPage(nextPage)
        }
    }

    return(
    <div className="landingpage2-container">
        <h1  className="header-text2"> Welcome to the world of LIGHT</h1>
        <Link to="/" style={{color:"white", fontWeight:"bold", marginBottom:"1em"}}>ALT 1</Link>
        {showInstructions ? 
                <div className="instruction-bubble2">
                    <div style={{width:"100%", justifyContent:"flex-end"}}>
                        <div onClick={closeInstructions} className="instruction-arrow__container2">
                                        <p className="instruction-arrow2 ">X</p>
                        </div>
                    </div>
                    <div className="instruction-text__container">
                        {page == 0 ?
                        <>
                            <p className="instruction-text2" style={{fontSize:"2.5em", textAlign:"center"}}>The Dungeon Master is glad to see you.</p>
                        </>
                        : null
                        }
                        {page == 1 ?
                        <>
                            <h2 className="instruction-text2" style={{ fontWeight:"bold", textAlign:"center"}}>Roleplay your Character</h2>
                            <p className="instruction-text2">
                                You will be teleported into our mystical realm and fill the shoes of a
                                character who lives there — playing that role you must act and talk with
                                other LIGHT denizens. As you interact, your messages will be evaluated by
                                the Dungeon Master AI. Portray your character well and you will increase
                                your <b>experience points</b>.
                            </p>
                            <p className="instruction-text2" >
                                Other characters will also be playing their roles as well — some of them
                                will be other human souls, others will be AIs. When everyone is playing
                                their role to the best of their ability in the realm the experience will
                                be maximized. You can <b>reward</b> other players when you are impressed
                                by their skills. You can also <b>report</b> or demote unwanted behaviors:
                                e.g., mentions of the real world, bad behavior. Stay good, my denizens!
                            </p>
                        </>
                        :null
                        }
                        {page == 2 ?
                        <>
                            <h2 className="instruction-text2" style={{ fontWeight:"bold", textAlign:"center"}}>Interact with the World</h2>
                            <p className="instruction-text2">
                            <b>Talking:</b> Talking is the most important part of playing your role in
                            the world. You can say, whisper, shout or tell something to other
                            individuals — all using free-form text, e.g.
                            <i>
                                tell the smithy “I’d love to own such a fine tool! It looks like
                                wonderful craftsmanship, well done!” </i
                            >.
                            </p>
                            <p className="instruction-text2">
                            <b>Emotes:</b> You can also express your emotions in the game with
                            <u>emote actions</u>, e.g. <i>smile, grin, scream</i> or <i>dance</i>.
                            </p>
                            <p className="instruction-text2">
                            <b>Actions:</b> You can move into new locations (e.g., <i>go west</i>),
                            pick up objects (e.g., <i>get tool</i>), give objects (e.g.,
                            <i>give tool to smithy</i>), wear clothing, wield weapons, eat, drink, try
                            to steal objects, and more. See <u>here</u> for the full list of actions.
                            </p>
                        </>
                        :null
                        }
                        <div className="arrowbox">
                                {
                                page !== 0 ?
                                <div onClick={()=>pageChangeHandler("-")} className="instruction-arrow__container2">
                                    <p className="instruction-arrow2">{"<"}</p>
                                </div>
                                : <div style={{width: "3em", margin: ".5em;"}}/>
                                }
                                {
                                page !== 2 ?
                                <div onClick={()=>pageChangeHandler("+")} className="instruction-arrow__container2 ">
                                    <p className="instruction-arrow2">{">"}</p>
                                </div>
                                : <div style={{width: "3em", margin: ".5em;"}}/>
                                }
                            </div>
                    </div>
                </div>
                : null
                }
            <div className="main-container2">
                <div className="menu-container2">
                    <Link style={{textDecoration:"none"}} to="/play">
                        <div className="menu-item2">
                            <h1 className="neon-text2">Play Now</h1>
                        </div>
                    </Link>
                    <div className="menu-item2">
                            <h1 onClick={openInstructions} className="neon-text2">Instructions</h1>
                        </div>
                    <Link style={{textDecoration:"none"}} to="/about2">
                        <div className="menu-item2">
                            <h1 className="neon-text2">About</h1>
                        </div>
                    </Link>
                </div>
            </div>
            <div className="terms-container">
                <h3 className="instruction-text2" style={{fontWeight:"bold"}}>Usage terms</h3>
                <p className="instruction-text2">
                    You should read our <a href="/terms">terms</a> regarding how we process
                    and use data that you send to LIGHT. You are accepting these terms by
                    playing the game.
                </p>
            </div>
        </div>
    )
}

export default LandingPage2