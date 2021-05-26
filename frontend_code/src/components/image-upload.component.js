import React, { Component } from "react";
import UploadService from "../services/file-upload.service";

export default class UploadImages extends Component {
  constructor(props) {
    super(props);
    this.selectFile = this.selectFile.bind(this);
    this.upload = this.upload.bind(this);

    this.state = {
      currentFile: undefined,
      previewImage: undefined,
      progress: 0,
      data: {
        address: "",
        country: "",
        dob: "",
        ethnicity: "",
        fullname: "",
        idc: "",
        national: "",
        sex: ""
      },
      value: 1,
      viewCode: `curl -X POST "http://0.0.0.0:8000/ekyc/detectwithstream" -H  "accept: application/json" -H  "Content-Type: multipart/form-data" -F "file=@232.jpg;type=image/jpeg";`,
    };
  }

  onChange = e => {
    this.setState({value: e.target.value});
    if (e.target.value === 1){
      this.setState({
        viewCode: `curl -X POST "http://0.0.0.0:8000/ekyc/detectwithstream" -H  "accept: application/json" -H  "Content-Type: multipart/form-data" -F "file=@232.jpg;type=image/jpeg";`
      })
    }
  };

  selectFile(event) {
    if (event.target.files[0]){
      this.setState({
        currentFile: event.target.files[0],
        previewImage: URL.createObjectURL(event.target.files[0]),
        progress: 0,
        message: ""
      });
      this.upload(event.target.files[0]);
    }
  }

  upload(fileSelect) {
    this.setState({
      progress: 0,
    });

    UploadService.upload(fileSelect, (event) => {
      this.setState({
        progress: Math.round((100 * event.loaded) / event.total),
      });
    })
      .then((response) => {
        this.setState({
          data: response.data,
        });
        // return UploadService.getFiles();
        return;
      })
      .catch((err) => {
        this.setState({
          progress: 0,
          data: "Could not upload the image!",
          currentFile: undefined,
        });
      });
  }

  render() {
    const {
      currentFile,
      previewImage,
      progress,
    } = this.state;

    return (
      <div className="row">
        <div className="col-12">
        <div className="row">
            <div className="col-8">
              <label className="btn btn-default p-0">
                <input type="file" accept="image/*" onChange={this.selectFile} />
              </label>
            </div>
            {currentFile && (
                <div className="progress my-3">
                  <div
                    className="progress-bar progress-bar-info progress-bar-striped"
                    role="progressbar"
                    aria-valuenow={progress}
                    aria-valuemin="0"
                    aria-valuemax="100"
                    style={{ width: progress + "%" }}
                  >
                    {progress}%
                  </div>
                </div>
              )}
          </div>
          <div className="row">
            <div className="col-6">

              {previewImage && (
                <div>
                  <img className="preview" src={previewImage} alt="previewImage" width="100%" />
                </div>
              )}
            </div>
            <div style={{display:'flex', flexDirection:'row'}} className="col-6">
              <div style={{width: 130}}>
              <div style={{fontWeight:"bold"}}>Id:</div>
              <div style={{fontWeight:"bold"}}>Name:</div>
              <div style={{fontWeight:"bold"}}>Sex:</div>
              <div style={{fontWeight:"bold"}}>DoB:</div>
              <div style={{fontWeight:"bold"}}>Nationality:</div>
              <div style={{fontWeight:"bold"}}>Country:</div>
              <div style={{fontWeight:"bold"}}>Address:</div>
              <div style={{fontWeight:"bold"}}>Ethnicity:</div>
              <div style={{fontWeight:"bold"}}>Type:</div>
              <div style={{fontWeight:"bold"}}>Score:</div>
              <div style={{fontWeight:"bold"}}>Time:</div>
              </div>
              <div>
              <div>{this.state.data.idc ? this.state.data.idc : "N/A"}</div>
              <div>{this.state.data.fullname ? this.state.data.fullname : "N/A"}</div>
              <div>{this.state.data.sex ? this.state.data.sex : "N/A"}</div>
              <div>{this.state.data.dob ? this.state.data.dob : "N/A"}</div>
              <div>{this.state.data.national ? this.state.data.national : "N/A"}</div>
              <div>{this.state.data.country ? this.state.data.country : "N/A"}</div>
              <div>{this.state.data.address ? this.state.data.address : "N/A"}</div>
              <div>{this.state.data.ethnicity ? this.state.data.ethnicity : "N/A"}</div>
              <div>{this.state.data.typekyc ? this.state.data.typekyc : "N/A"}</div>
              <div>{this.state.data.score ? this.state.data.score : "N/A"}</div>
              <div>{this.state.data.totaltime ? this.state.data.totaltime : "N/A"}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }
}
