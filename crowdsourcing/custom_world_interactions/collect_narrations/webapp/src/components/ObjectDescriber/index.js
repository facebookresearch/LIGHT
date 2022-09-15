import React, {useEffect, useState} from "react";
import "./styles.css";


const ObjectDescriber = ({ name, description, onChangeName, onChangeDescription}) => {
    return (
      <div className="form-container">
        <h1 className="describer-header">Primary Item: </h1>
        Name:
        <textarea
          as="textarea"
          className="description-form"
          rows={1}
          placeholder="Please come up with a setting-appropriate object you'll use with the above!"
          onChange={(e) => onChangeName(e.target.value)}
          value={name}
        />
        <br/>
        Description:
        <textarea
          as="textarea"
          className="description-form"
          rows={3}
          placeholder="Please provide a description for your object."
          onChange={(e) => onChangeDescription(e.target.value)}
          value={description}
        />
      </div>
    );
}
export default ObjectDescriber;
