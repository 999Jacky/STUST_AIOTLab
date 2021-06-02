package main

import (
	"bytes"
	"encoding/base64"
	"encoding/json"
	"fmt"
	"io"
	"io/ioutil"
	"mime/multipart"
	"net/http"
	"net/url"
)

var SendCtl bool

var Did int
var Pid int

var MedsInfo map[string]bool

func RecvMsg(data map[string]interface{}) {
	if data["function"] == "Img" {
		imgBase64 := data["Img"].(string)
		Log.Debugln("Get Img Len:", len(imgBase64))
		SendImg(imgBase64)
		ddd, _ := base64.StdEncoding.DecodeString(imgBase64)
		ioutil.WriteFile("./output.jpg", ddd, 0666)
	}
}

func SendImg(img string) {
	if SendCtl {
		// if true {
		// Post IMG
		SendCtl = false
		u := url.Values{}
		u.Set("img", img)
		resp, err := http.PostForm("http://"+DetectionServerIP+"/detection", u)
		if err != nil {
			return
		}
		defer resp.Body.Close()
		body, err := ioutil.ReadAll(resp.Body)
		if err != nil {
			Log.Errorln(err)
			return
		}
		// Log.Debugln(string(body))
		j := map[string]interface{}{}
		json.Unmarshal(body, &j)
		SendResult(j)
	} else {
		Log.Infoln("Drop Img")
	}
}

func SendResult(data map[string]interface{}) {
	// img:string,meds:(string,flot64),status:bool
	meds := make([]string, 0)

	for i := range data["Meds"].(map[string]interface{}) {
		meds = append(meds, i)
	}

	WriteJson2Backend(BackendWsMsg{
		Function: DetectionDoneCMD,
		Data: map[string]interface{}{
			"PID":        Pid,
			"machine":    BoxMd5Mac,
			"resultList": meds,
		},
	})
	UploadResultImg(data["img"].(string))
}

func UploadResultImg(imgBas64 string) {
	unbased, err := base64.StdEncoding.DecodeString(imgBas64)
	if err != nil {
		Log.Errorln(err)
	}
	img := bytes.NewReader(unbased)
	for Did == -1 {
	}
	body := &bytes.Buffer{}
	writer := multipart.NewWriter(body)
	imgFile, _ := writer.CreateFormFile("file", "img_"+fmt.Sprint(Did)+".jpg")
	io.Copy(imgFile, img)
	writer.Close()
	req, err := http.NewRequest(http.MethodPost, "http://"+BackendServerIP+"/upload", body)
	req.Header.Set("Content-Type", writer.FormDataContentType())

	if err != nil {
		Log.Errorln(err)
	}
	_, err = http.DefaultClient.Do(req)
	if err != nil {
		Log.Errorln(err)
	}
	Log.Debugln("Send Img Done")
}
