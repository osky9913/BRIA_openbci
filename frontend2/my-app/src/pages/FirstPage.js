import React from 'react';
import { Button, Flex } from 'antd';

const FirstPage = ({ onStart }) => {
  return (
    <div style={{ textAlign: 'center', marginTop: '100px' }}>

    <Flex vertical>
      <div>  
      <img src="/brain.png" alt="Brain Logo" style={{ maxWidth: '600px', marginBottom: '20px' }} />
      </div>
      <div>
      <Button type="primary" onClick={onStart}>
        Get Started
      </Button>
      </div>
    </Flex>  
    </div>
  );
};

export default FirstPage;
