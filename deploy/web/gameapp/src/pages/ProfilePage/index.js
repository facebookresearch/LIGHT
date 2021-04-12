import React from "react";

import "./styles.css";

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
      <div className="profiledata-container" style={{ color: "gold" }}>
        <div>
          <h3 style={{ color: "gold" }}>TOTAL EXP EARNED:</h3>
          <h3>TOTAL EXP GIVEN:</h3>
        </div>
        <div className="table-container"></div>
      </div>
      <div className="profiledata-container" style={{ color: "gold" }}>
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
  );
};

export default ProfilePage;
