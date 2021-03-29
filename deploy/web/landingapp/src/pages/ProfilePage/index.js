import React from "react";
import { Link } from "react-router-dom";

import "../../styles.css";

import PortraitPlaceholder from "../../assets/images/scribe.png";

const ProfilePage = (props) => {
  const roleData = [
    { role: "Rat", experience: 20 },
    { role: "Grave Digger", experience: 10 },
    { role: "Bandit", experience: 100 },
  ];

  return (
    <div className="profilepage-container">
      <div className="nameplate-container">
        <img className="nameplate-portrait" src={PortraitPlaceholder} />
        <div className="nameplate">
          <h3 style={{ textAlign: "center" }}>
            {props.username || "USER NAME"}
          </h3>
        </div>
      </div>
      <div className="profiledata-container">
        <div className="profiledata-section">
          <table>
            <tr>
              <th>Name</th>
              <th> Joe Doe</th>
            </tr>
            <tr>
              <th>Email</th>
              <th>jd@jd.net</th>
            </tr>
            <tr>
              <th>Location</th>
              <th>North America</th>
            </tr>
            <tr>
              <th>Password</th>
              <th>******</th>
            </tr>
            <tr>
              <th>Location</th>
              <th>North America</th>
            </tr>
          </table>
          <div className="biodata-container">
            <h4>Bio</h4>
            <p>
              Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do
              eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut
              enim ad minim veniam, quis nostrud exercitation ullamco laboris
              nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in
              reprehenderit in voluptate velit esse cillum dolore eu fugiat
              nulla pariatur. Excepteur sint occaecat cupidatat non proident,
              sunt in culpa qui officia deserunt mollit anim id est laborum.
            </p>
          </div>
        </div>
        <div className="profiledata-section">
          <div className="table-container">
            <h1>GAMEPLAY STATS</h1>
            <table>
              <tr>
                <th>Role</th>
                <th>XP</th>
              </tr>
              {roleData.length
                ? roleData.map((data) => (
                    <tr>
                      <td>{data.role}</td>
                      <td>{data.experience}</td>
                    </tr>
                  ))
                : null}
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;
