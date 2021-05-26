import React from "react";
import "./App.css";
import "bootstrap/dist/css/bootstrap.min.css";
import { Tabs } from 'antd';
import "antd/dist/antd.css";
import { Radio } from 'antd';
import UploadImages from "./components/image-upload.component";

const { TabPane } = Tabs;

function callback(key) {
  console.log(key);
}

function App() {
  return (
    <div className="container_body">
        <h1>  <img className="preview" src="https://photocloud.mobilelab.vn/2021-05-07/5bba5fbf-31c9-4eb9-a32b-8f40d63de61e.png" alt="icon" width="3%" /> AI Reader - Vietnamese ID Card Recognition </h1>
        <Tabs defaultActiveKey="1" onChange={callback} style={{fontSize:18}}>
          <TabPane tab="Overview" key="2" style={{fontSize:18}}>
          AI Reader - Vietnamese ID Card Recognition
          </TabPane >
          <TabPane tab="Service" key="1" style={{fontSize:18}}>
            <UploadImages />
          </TabPane>
          <TabPane tab="Document" key="3" style={{fontSize:18}}>
            <div className="container_body">
              <h3>API</h3>
              <div className="row">
                <Radio.Group value="1">
                  <Radio value={1} style={{fontSize:20}}>cUrl</Radio>
                </Radio.Group>
              </div>
              <div className="row">
                <code>
                curl -X POST "http://0.0.0.0:8000/ekyc/detectwithstream" 
                -H  "accept: application/json" 
                -H  "Content-Type: multipart/form-data" 
                -F "file=@232.jpg;type=image/jpeg";
                </code>
              </div>
            </div>
          </TabPane>
        </Tabs>
    </div>
  );
}

export default App;
