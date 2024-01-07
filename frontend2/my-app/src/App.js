import React, { useState } from "react";
import FirstPage from "./pages/FirstPage";
import SecondPage from "./pages/SecondPage";
import "./App.css"; // Assuming the CSS is defined here

function App() {
  const [currentPage, setCurrentPage] = useState("first");
  const [animate, setAnimate] = useState(false);

  const handleStart = () => {
    setAnimate(true);
    fetch("http://localhost:8000/prepare_stream", {
      method: "GET", // or 'POST' if you're sending data
      // Include other necessary headers or body data
    })
      .then((response) => response.json())
      .then((data) => {
        // Handle the received data (e.g., display the image)
      })
      .catch((error) => {
        // Handle any errors
      });
    setTimeout(() => setCurrentPage("second"), 500);
  };

  return (
    <div>
      {currentPage === "first" && <FirstPage onStart={handleStart} />}
      {currentPage === "second" && (
        <div className={animate ? "fadeIn" : ""}>
          <SecondPage />
        </div>
      )}
    </div>
  );
}

export default App;
