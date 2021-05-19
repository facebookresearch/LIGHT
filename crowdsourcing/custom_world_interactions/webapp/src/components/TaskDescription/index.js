import React from "react";
import "./styles.css";

//CUSTOM COMPONENTS
import GoodExampleList from "./GoodExampleList";
import BadExampleList from "./BadExampleList";


const TaskDescription = ()=> {
  return (
    <>
      <div className="description-container">
        <div className="description-section">
          <p className="description-section__label">
            Overview:
          </p>
          <p className="description-section__text">
            We're trying to crowdsource interactions between two objects. These interactions will be set in a <b>medieval fantasy scenario</b>, and as such should <b>not refer to real people, places, or modern day technologies.</b> Ultimately, we'll want someone to be able to select two objects and be told the outcome of them using these objects together, in a second-person <i>"choose your adventure"</i> narrative style.
          </p>
        </div>
        <div className="description-section">
          <p className="description-section__label">
            Details:
          </p>
          <div className="description-subsection">
            <p className="description-section__text">
              For this, we define an <span style={{color:"green"}}><b>interaction</b></span> as something that can be done with two entities. Here we'll call them the <span style={{color:"gold"}} ><b> Primary </b></span> entity and the <span style={{color:"blue"}} ><b> Secondary </b></span> entity, and they have distinct characteristics.  Using the Primary and Secondary entities, you should then come up with an interaction that may occur if some actor where to try to use the two entities together. This interaction should be in second-person, as if you were narrating the outcome to that actor. The interaction should be directly between both entities, but a direct action of the actor, and should be appropriate for a medieval fantasy adventure. The interaction should only involve the actor, the two entities, and possibly something directly created by the two things interacting. Do not assume that other entities exist or use them in your narration.
            </p>
            <div className="description-section">
              <p className="description-section__label">
                <span style={{color:"gold"}} ><b>Primary: </b></span>
              </p>
              <p className="description-section__text">
                Should be an object that a person can hold or physically move.
              </p>
            </div>
            <div className="description-section">
              <p className="description-section__label">
                <span style={{color:"blue"}} ><b>Secondary: </b></span>
              </p>
              <p className="description-section__text">
                Can be any entity that a person could use the primary object with, can be held (but doesn't necessarily have to be), and may be a living thing.
              </p>
            </div>
          </div>
        </div>
        <div className="description-section">
          <p className="description-section__label">
            <b>For example:</b>
          </p>
          <p className="description-section__text">
            Let's say we have a  <b>fire torch </b> as the <span style={{color:"gold"}} ><b> primary object </b></span> and a
            <b> wooden table</b> as the <span style={{color:"blue"}} ><b>  secondary object</b></span>.
            In this case, a good action <span style={{color:"green"}}><b> description </b></span>  would be:{" "}
            <span style={{color:"green"}}><i>
              "You light the <span style={{color:"blue"}} ><b> table </b></span> on fire with <span style={{color:"gold"}} ><b>the torch </b></span>. It ignites and burns to
              the ground, leaving a pile of ash."
            </i></span>
          </p>
        </div>
      </div>
      <br />
      <div className="examples-container">
        <GoodExampleList/>
        <BadExampleList/>
      </div>
      <div className="note-container">
          <p className="note-text">
            <b>* </b> Avoid submitting interactions which are physically impossible or
            nonsense in the current scenario. Interactions must also be written in
            second person.
          </p>
        </div>
    </>
  );
}

export default TaskDescription;
