//REACT
import React from "react";
//STYLING
import "./styles.css"

// loadingScreen - what will be rendered when mephisto isLoading prop is true
const LoadingScreen = ()=> {
  return (
    <section className="hero is-light">
      <div className="hero-body">
        <div className="container">
          <p className="subtitle is-5">Loading...</p>
        </div>
      </div>
    </section>
  );
}

export default LoadingScreen;