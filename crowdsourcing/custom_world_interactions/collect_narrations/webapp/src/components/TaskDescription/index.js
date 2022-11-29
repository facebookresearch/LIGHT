import React from "react";
import "./styles.css";

import TaskExample from "../../assets/images/TaskExample.png";
//CUSTOM COMPONENTS
import GoodExampleList from "./GoodExampleList";
import BadExampleList from "./BadExampleList";

const goalFailingTaskDescription = () => {
  return (
    <>
      <div className="description-container">
        <div className="description-section">
          <p className="description-section__label">
            Overview:
          </p>
          <p className="description-section__text">
            We're trying to crowdsource interactions a character may enact between two objects. These interactions will be set in a <b>medieval fantasy scenario</b>, and as such should <b>not refer to real people, places, or modern day technologies.</b> Ultimately, we'll want someone to be able to select two objects and be told the outcome of them using these objects together, in a second-person <i>"choose your adventure"</i> narrative style. In this task we want to collect interactions that fail to occur.
          </p>
        </div>
        <div className="description-section">
          <p className="description-section__label">
            Details:
          </p>
          <div className="description-subsection">
            <p className="description-section__text">
              For this, we define an <span style={{color:"green"}}><b>interaction</b></span> as something that can be done with two entities. Here we'll call them the <span style={{color:"gold"}} ><b> Primary </b></span> entity and the <span style={{color:"blue"}} ><b> Secondary </b></span> entity, and they have distinct characteristics.
            </p>
              <div className="description-section" style={{paddingBottom:0}}>
              <p className="description-section__label">
                <span style={{color:"gold"}} ><b>Primary: </b></span>
              </p>
              <p className="description-section__text">
                Should be an object that a person can hold or physically move. You will come up with an interesting primary entity.
              </p>
            </div>
            <div className="description-section">
              <p className="description-section__label">
                <span style={{color:"blue"}} ><b>Secondary: </b></span>
              </p>
              <p className="description-section__text">
                One of a provided list of objects. May or may not be held by the actor, but should be involved in the interaction with the primary entity.
              </p>
            </div>
            <p className="description-section__text">
              Using the Primary and Secondary entities, you should then come up with an interaction that an actor may attempt between two objects, but should be impossible. The description of the failure should be in second person, as if you were narrating the outcome to that actor. The suggested interaction should be directly between both entities, but a direct action of the actor, and should be appropriate for a medieval fantasy adventure. The interaction should only involve the actor and the two entities. Do not assume that other entities exist or use them in your narration.  After selecting an object it's description will appear, when narrating this interaction feel free to include details from this description but do not add attributes or context to the objects.  Remember the interaction you are narrating is <b>between </b>the two objects.
            </p>
            <p className="description-section__text">
              <b>ADDITIONAL INSTRUCTIONS:</b> The goal at the moment is to collect <i>failing</i> interactions between objects that <b>can't successfully interact with one another in the intended way</b>, meaning ones where the outcome of the event is only the narration, and the descriptions, locations, and state of the other objects shouldn't change as a result of the interaction. See the below for an example.
            </p>
          </div>
        </div>
        <div className="description-section">
          <p className="description-section__label">
            <b>For example:</b>
          </p>
          <p className="description-section__text">
            Let's say you select a <b>river</b> as the <span style={{color:"blue"}} ><b>  secondary object</b></span>. It has the provided description:
            "The river is a bright blue and runs north to south. You can see little fish beneath the ripples."
            In this case, you may consider a <b>match</b> as the primary object, given it doesn't have a clear meaningful interaction with a rock. Then a good <span style={{color:"green"}}><b>action phrase </b></span> for this failing interaction would
            be:{" "}
            <span style={{color:"green"}}><i>
              "Ignite <span style={{color:"blue"}} ><b> river </b></span> with the <span style={{color:"gold"}} ><b>match </b></span>." {" "}
            </i></span>
            Using this action phrase, a good action <span style={{color:"green"}}><b> description </b></span>  would be:{" "}
            <span style={{color:"green"}}><i>
              "You cannot successfully light a river on fire, especially not with a match! All you'd be left with is a soggy wooden stick. You choose not to ruin the match."
            </i></span>
          </p>
        </div>
      </div>
      <div className="description-row">
        <img src={TaskExample} className="example-img" />
      </div>
      <br />
      <p>
        More good and bad examples are listed below to help you get a feel for the type of interactions we're looking for. These however
        don't capture the failing nature we're looking for in this iteration of the task, and instead show the style and context
        considerations to watch out for.
      </p>
      <div className="examples-container">
        <GoodExampleList/>
        <BadExampleList/>
      </div>
      <div className="note-container">
          <p className="note-text">
            <b>* </b> The description for interaction failure must be written in second person.
          </p>
        </div>
    </>
  );
}

const goalSimpleTaskDescription = () => {
  return (
    <>
      <div className="description-container">
        <div className="description-section">
          <p className="description-section__label">
            Overview:
          </p>
          <p className="description-section__text">
            We're trying to crowdsource interactions a character may enact between two objects. These interactions will be set in a <b>medieval fantasy scenario</b>, and as such should <b>not refer to real people, places, or modern day technologies.</b> Ultimately, we'll want someone to be able to select two objects and be told the outcome of them using these objects together, in a second-person <i>"choose your adventure"</i> narrative style.
          </p>
        </div>
        <div className="description-section">
          <p className="description-section__label">
            Details:
          </p>
          <div className="description-subsection">
            <p className="description-section__text">
              For this, we define an <span style={{color:"green"}}><b>interaction</b></span> as something that can be done with two entities. Here we'll call them the <span style={{color:"gold"}} ><b> Primary </b></span> entity and the <span style={{color:"blue"}} ><b> Secondary </b></span> entity, and they have distinct characteristics.
            </p>
              <div className="description-section" style={{paddingBottom:0}}>
              <p className="description-section__label">
                <span style={{color:"gold"}} ><b>Primary: </b></span>
              </p>
              <p className="description-section__text">
                Should be an object that a person can hold or physically move. You will come up with an interesting primary entity.
              </p>
            </div>
            <div className="description-section">
              <p className="description-section__label">
                <span style={{color:"blue"}} ><b>Secondary: </b></span>
              </p>
              <p className="description-section__text">
                One of a provided list of objects. May or may not be held by the actor, but should be involved in the interaction with the primary entity.
              </p>
            </div>
            <p className="description-section__text">
              Using the Primary and Secondary entities, you should then come up with an interaction that may occur if some actor where to try to use the two entities together. This interaction should be in second-person, as if you were narrating the outcome to that actor. The interaction should be directly between both entities, but a direct action of the actor, and should be appropriate for a medieval fantasy adventure. The interaction should only involve the actor and the two entities. Do not assume that other entities exist or use them in your narration.  After selecting an object it's description will appear, when narrating this interaction feel free to include details from this description but do not add attributes or context to the objects.  Remember the interaction you are narrating is <b>between </b>the two objects.
            </p>
            <p className="description-section__text">
              <b>ADDITIONAL INSTRUCTIONS:</b> The goal at the moment is to collect <i>simple</i> interactions between objects that <b>don't interact with one another in a meaningful or substantial way</b>, meaning ones where the outcome of the event is only the narration, and the descriptions, locations, and state of the other objects shouldn't change as a result of the interaction. See the below for an example.
            </p>
          </div>
        </div>
        <div className="description-section">
          <p className="description-section__label">
            <b>For example:</b>
          </p>
          <p className="description-section__text">
            Let's say you select a <b>rock</b> as the <span style={{color:"blue"}} ><b>  secondary object</b></span>. It has the provided description:
            "This rock is heavy and solid, but is otherwise uninteresting."
            In this case, it would be reasonable to provide a <b>metal spoon</b> as the primary object, given it doesn't have a clear meaningful interaction with a rock. Then a good <span style={{color:"green"}}><b>action phrase </b></span> for this task would
            then be:{" "}
            <span style={{color:"green"}}><i>
              "Tap <span style={{color:"blue"}} ><b> rock </b></span> with the <span style={{color:"gold"}} ><b>metal spoon </b></span>." {" "}
            </i></span>
            Using this action phrase, a good action <span style={{color:"green"}}><b> description </b></span>  would be:{" "}
            <span style={{color:"green"}}><i>
              "You tap the <span style={{color:"blue"}} ><b> rock </b></span> with the <span style={{color:"gold"}} ><b>spoon </b></span>. It makes a pleasant 
              'dink' sound. You don't think spoon-rock drumming will catch on anytime soon though."
            </i></span>
          </p>
        </div>
      </div>
      <div className="description-row">
        <img src={TaskExample} className="example-img" />
      </div>
      <br />
      <p>
        More good and bad examples are listed below to help you get a feel for the type of interactions we're looking for. These however
        don't capture the simplistic nature we're looking for in this iteration of the task, and instead show the style and context
        considerations to watch out for.
      </p>
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

const BaseTaskDescription = () => {
  return (
    <>
      <div className="description-container">
        <div className="description-section">
          <p className="description-section__label">
            Overview:
          </p>
          <p className="description-section__text">
            We're trying to crowdsource interactions a character may enact between two objects. These interactions will be set in a <b>medieval fantasy scenario</b>, and as such should <b>not refer to real people, places, or modern day technologies.</b> Ultimately, we'll want someone to be able to select two objects and be told the outcome of them using these objects together, in a second-person <i>"choose your adventure"</i> narrative style.
          </p>
        </div>
        <div className="description-section">
          <p className="description-section__label">
            Details:
          </p>
          <div className="description-subsection">
            <p className="description-section__text">
              For this, we define an <span style={{color:"green"}}><b>interaction</b></span> as something that can be done with two entities. Here we'll call them the <span style={{color:"gold"}} ><b> Primary </b></span> entity and the <span style={{color:"blue"}} ><b> Secondary </b></span> entity, and they have distinct characteristics.
            </p>
              <div className="description-section" style={{paddingBottom:0}}>
              <p className="description-section__label">
                <span style={{color:"gold"}} ><b>Primary: </b></span>
              </p>
              <p className="description-section__text">
                Should be an object that a person can hold or physically move. You will come up with an interesting primary entity.
              </p>
            </div>
            <div className="description-section">
              <p className="description-section__label">
                <span style={{color:"blue"}} ><b>Secondary: </b></span>
              </p>
              <p className="description-section__text">
                One of a provided list of objects. May or may not be held by the actor, but should be involved in the interaction with the primary entity.
              </p>
            </div>
            <p className="description-section__text">
              Using the Primary and Secondary entities, you should then come up with an interaction that may occur if some actor where to try to use the two entities together. This interaction should be in second-person, as if you were narrating the outcome to that actor. The interaction should be directly between both entities, but a direct action of the actor, and should be appropriate for a medieval fantasy adventure. The interaction should only involve the actor, the two entities, and possibly something directly created by the two things interacting. Do not assume that other entities exist or use them in your narration.  After selecting an object it's description will appear, when narrating this interaction feel free to include details from this description but do not add attributes or context to the objects.  Remember the interaction you are narrating is <b>between </b>the two objects.
            </p>
          </div>
        </div>
        <div className="description-section">
          <p className="description-section__label">
            <b>For example:</b>
          </p>
          <p className="description-section__text">
            Let's say you select a <b> wooden table</b> as the <span style={{color:"blue"}} ><b>  secondary object</b></span>. It has the provided description:
            "This wooden table has seen better days - in fact the history of those days appears to have been etched right into the surface by previous patrons."
            In this case, it would be reasonable to provide a <b>lit torch</b> as the primary object. A good action <span style={{color:"green"}}><b> phrase </b></span>  would
            then be:{" "}
            <span style={{color:"green"}}><i>
              "Ignite the <span style={{color:"blue"}} ><b> table </b></span> with the <span style={{color:"gold"}} ><b>lit torch </b></span>." {" "}
            </i></span>
            Using this action phrase, a good action <span style={{color:"green"}}><b> description </b></span>  would be:{" "}
            <span style={{color:"green"}}><i>
              "You light the <span style={{color:"blue"}} ><b> table </b></span> on fire with the <span style={{color:"gold"}} ><b>lit torch </b></span>. It ignites and burns,
              gradually reducing the table and all the carvings on it to a pile of ash on the ground."
            </i></span>
          </p>
        </div>
      </div>
      <div className="description-row">
        <img src={TaskExample} className="example-img" />
      </div>
      <br />
      <p>
        More good and bad examples are listed below to help you get a feel for the type of interactions we're looking for.
      </p>
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

const TaskDescription = goalFailingTaskDescription;

export default TaskDescription;
