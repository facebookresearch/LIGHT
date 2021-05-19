import React from "react";
import "./styles.css";

//CUSTOM COMPONENTS
import GoodExampleList from "./GoodExampleList";
import BadExampleList from "./BadExampleList";


const TaskDescription = ()=> {
  return (
    <>
      <div className="description-container">
        <p>
          We're trying to crowdsource interactions between two objects. These interactions will be set in a medieval fantasy scenario, and as such should not refer to real people, places, or modern day technologies. Ultimately, we'll want someone to be able to select two objects and be told the outcome of them using these objects together, in a second-person "choose your adventure" narrative style.
        </p>
        <p>
          After that, write a simple <b>interaction</b> between these two objects
          in the textbox.
        </p>
        <br />
        <p>
          For this, we define an interaction as something that can be done with two entities. Here we'll call them the "Primary" entity and the "Secondary" entity, and they have distinct characteristics.
          Primary: Should be an object that a person can hold or physically move.
          Secondary: Can be any entity that a person could use the primary object with. Can be held, but doesn't necessarily have to be. May be a living thing.
        </p>
        <br />
        <p>
          For example, let's say we have a fire torch as the primary object and a
          wooden table as the secondary object.
        </p>
        <p>
          In this case, a good action description would be:{" "}
          <i>
            "You light the table on fire with the torch. It ignites and burns to
            the ground, leaving a pile of ash."
          </i>
        </p>
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
