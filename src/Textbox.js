import React, { useState } from "react";
import "./Textbox.css";

function TextBox() {
  const [inputValue, setInputValue] = useState("");
  const [submittedValue, setSubmittedValue] = useState("");

  const handleChange = (event) => {
    setInputValue(event.target.value);
  };

  const handleKey = (event) => {
    if (event.key === "Enter") {
      setSubmittedValue(inputValue);
      console.log(inputValue);
    }
  };

  return (
    <div className="center-container">
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
