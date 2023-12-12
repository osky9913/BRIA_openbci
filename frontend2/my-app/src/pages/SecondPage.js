import React, { useState } from "react";
import { Button, Flex } from "antd";
import Eeg from "../Eeg";
import Test from "../Test";
import EEGD3 from "../EEGD3";

function SecondPage() {
  // eslint-disable-next-line no-undef
  const [eegButton, setEegButton] = useState(false);
  const [eegButtonD3, setEegButtonD3] = useState(false);

  return (
    <div style={{ textAlign: "center", marginTop: "100px" }}>
      <Flex>
        <div style={{ minWidth: "400px", maxWidth: "400px" }}>
          {eegButton && <Eeg />}
        </div>
        <div style={{ minWidth: "400px", maxWidth: "400px" }}>
          {eegButtonD3 && <EEGD3 />}
        </div>
        <div>
          <Flex>
            <div>
              <Button type="primary" onClick={() => setEegButton(true)}>
                EEG Graph
              </Button>
            </div>
            <div>
              <Button type="primary" onClick={() => setEegButtonD3(true)}>
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
