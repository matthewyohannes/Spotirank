import React, { useState, useEffect } from "react";
import "./App.css";

const App = () => {
  const [loggedIn, setLoggedIn] = useState(false);
  const [topArtists, setTopArtists] = useState([]);

  useEffect(() => {
    // check if the user is logged in when the component mounts
    checkLoggedIn();
  }, []);

  const checkLoggedIn = async () => {
    try {
      // check if the user is logged in by making a request to Flask backend's checkLoggedIn endpoint
      const response = await fetch("/checkLoggedIn");
      if (response.ok) {
        setLoggedIn(true);
        // if user is logged in, fetch top artists
        fetchTopArtists();
      } else if (response.status === 401) {
        // If unauthorized, redirect to login page
        window.location.href = "http://localhost:5000/refresh-token";
      }
    } catch (error) {
      console.error("Error checking login status:", error);
    }
  };

  const fetchTopArtists = async () => {
    try {
      // fetch top artists data from Flask backend
      const response = await fetch("/topartists");
      if (response.ok) {
        const data = await response.json();
        setTopArtists(data.items);
      }
    } catch (error) {
      console.error("Error fetching top artists:", error);
    }
  };
  
  const artistInfo = topArtists.map((person) => (
    <li key={person.id}>
      <div className="artist-card">
        <img
          src={person.images[2].url}
          alt={person.name}
          className="artist-image"
        />
        <div className="artist-info">
          <p className="artist-name">{person.name}</p>
        </div>
      </div>
    </li>
  ));

  return (
    <div className="artist-container">
      <article>
        <h1>
          Welcome to Spotirank!
          <br />
          Here are your Top Artists
        </h1>
        <h5>This data is from the last 4 weeks!</h5>
        {artistInfo}
      </article>
    </div>
  );
};

export default App;