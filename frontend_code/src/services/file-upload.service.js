import http from "../http-common";

class FileUploadService {
  upload(file, onUploadProgress) {

    console.log(file)

    let formData = new FormData();

    formData.append("file", file);

    return http.post("/ekyc/detectwithstream", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
      onUploadProgress,
    });
  }

  getFiles() {
    return http.get("/files");
  }
}

export default new FileUploadService();