import React, { useState } from "react";
import "./Textbox.css";
import ServerResponse from "./ServerResponse";

function TextBox() {
  const [inputValue, setInputValue] = useState("");
  const [serverResponse, setServerResponse] = useState("Waiting for response");

  const handleChange = (event) => {
    setInputValue(event.target.value);
  };

  const handleKey = async (event) => {
    if (event.key === "Enter") {
      try {
        const response = await fetch("http://localhost:5001/api/data", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ message: inputValue }),
        });

        const result = await response.json();
        console.log("Response from server:", result);

        if (result.success) {
          setServerResponse(result.serverMessage);
        } else {
          setServerResponse("Error: Could not process your request.");
        }

        setInputValue("");
      } catch (error) {
        console.error("Error sending data to the server:", error);
        setServerResponse("Error: Could not reach the server.");
      }
    }
  };

  return (
    <div className="center-container">
      <ServerResponse message={serverResponse} />
      <input
        type="text"
        value={inputValue}
        onChange={handleChange}
        onKeyDown={handleKey}
        className="large-textbox"
        placeholder="Type something"
      />
    </div>
  );
}

export default TextBox;
