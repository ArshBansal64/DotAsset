import React from "react";
import "./ServerResponse.css";

function ServerResponse({ message }) {
  return (
    <div className="response-container">
      {/* If 'message' is truthy, display it; otherwise 'No response yet.' */}
      {message ? <p>{message}</p> : <p>No response yet.</p>}
    </div>
  );
}

export default ServerResponse;
