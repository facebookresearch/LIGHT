import React from "react";

function TaskDescription() {
    return (
      <div>
      <div className="title is-3">
        Constraints and Events Quiz Task
      </div>
        <p>We're trying to crowdsource possible interactions between a set of items. These interactions are set in a <b>medieval fantasy scenario</b>, and as such should not refer to real people, places, or modern day technologies. 
        In this task you will be given an interaction between two objects and then answer questions related to that event.</p>
        <br />
        <p>Try to be creative with the answers! Think that objects have certain attributes like "burned", "rotten", etc. Some attributes are <b>numeric</b> (Price, health) while some are in a <b>true/false</b> format (burned = True, rotten = false).</p> 
        <br />
        <p>For example, let's say we have the description "You light the table on fire with the torch. It ignites and burns to the ground, leaving a pile of ash.".</p>
        <br />
        <h2><b>Good Examples of Constraints and Events:</b></h2>
        <br />
        <div>
          <ul>
            <li><i>Is Holding Constraint?</i> <b>True</b> - the actor needs to be holding the torch</li>
            <li><i>Is the actor doing the action with a certain object?</i> <b>True</b> - this action cannot be done with any object. Some objects are not burneable</li>
            <li><i>Is the action being done with an agent?</i> <b>False</b> - this action target is a table, not a living being.</li>
            <li><i>Is the action being done within a specific room?</i> <b>False</b> - this action can happen anywhere with a torch and a wooden table.</li>
            <li><i> Does this action requires that an element involved (The actor or one of the objects) has an attribute restriction?</i> <b>True</b> - Wooden Table needs to have, for example, the attribute <i>burnable</i> = True. <b>You can (And are encouraged to) be creative answering this question!</b></li>
          </ul>
          <br/>
          <ul>
            <li><i>An entity is created?</i> <b>True</b> - an pile of ash is created.</li>
            <li><i>How others see this event?</i> <b>True</b> - "Actor lit the table on fire with the torch. It ignites and burns to the ground, leaving a pile of ash".</li>
            <li><i>IDoes this action modifies an attribute of something involved in it?</i> <b>True</b> - Now the attribute burned = True.</li>
          </ul>
        </div>
        <br />
        <p>Avoid submitting interactions which are physically impossible or nonsense in the current scenario.</p>
        <div>
        <br />
      </div>
    </div>
    );
  }

  export { TaskDescription };