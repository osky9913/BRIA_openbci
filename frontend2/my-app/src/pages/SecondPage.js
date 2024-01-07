import React, { useState } from "react";
import { Button, Flex } from "antd";
import Eeg from "../Eeg";
import EEGD3 from "../EEGD3";

function SecondPage() {
  // State to track which component is selected
  const [selectedComponent, setSelectedComponent] = useState(null);

  // Function to handle button click
  const handleButtonClick = (component) => {
    setSelectedComponent(component);
  };

  return (
    <div style={{ textAlign: "center", marginTop: "100px" }}>
      <Flex>
        <div style={{ minWidth: "400px", maxWidth: "400px" }}>
          {selectedComponent === "Eeg" && <Eeg />}
          {selectedComponent === "EEGD3" && <EEGD3 />}
        </div>
        <div>
          <Flex>
            <div>
              <Button type="primary" onClick={() => handleButtonClick("Eeg")}>
                EEG Graph
              </Button>
            </div>
            <div>
              <Button type="primary" onClick={() => handleButtonClick("EEGD3")}>
                EEG Graph D3
              </Button>
            </div>
          </Flex>
        </div>
      </Flex>
    </div>
  );
}

export default SecondPage;
