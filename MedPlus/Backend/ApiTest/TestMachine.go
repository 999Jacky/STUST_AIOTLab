package main

import (
	"bytes"
	"fmt"
	"github.com/gorilla/websocket"
	"golang.org/x/image/font"
	"golang.org/x/image/font/basicfont"
	"golang.org/x/image/math/fixed"
	"image"
	"image/color"
	"image/jpeg"
	"log"
	"mime/multipart"
	"net/http"
	"net/url"
	"strconv"
)

var Ws *websocket.Conn
var DOERR bool = false
var Url url.URL

var recvMedList []string
var DID float64 = -1
var Done bool = false

func init() {
	recvMedList = make([]string, 0)
}

func main() {
	Url = url.URL{Scheme: "ws", Host: "127.0.0.1:3000", Path: "/ws"}
	var err error
	Ws, _, err = websocket.DefaultDialer.Dial(Url.String(), nil)
	if err != nil {
		log.Fatalln(err)
	}
	go ReadMsg(Ws)
	Ws.WriteJSON(WsMsg{
		Function: "machine",
		Status:   false,
		Data: map[string]string{
			"machineID": "MAC",
		},
	})

	for {
		Done = false
		DOERR = !DOERR
		recvMedList = make([]string, 0)
		fmt.Println("Wait Input...")
		fmt.Scanln()
		Ws.WriteJSON(WsMsg{
			Function: "getPrescription",
			Status:   false,
			Data: map[string]interface{}{
				"PID": 1,
			},
		})
		for !Done {

		}
	}
}

func sendInfo() {
	sendList := make([]string, 0)
	if DOERR {
		if len(recvMedList) != 1 {
			sendList = append(sendList, recvMedList[0])
		}
	} else {
		sendList = recvMedList
	}
	Ws.WriteJSON(WsMsg{
		Function: "detection",
		Status:   false,
		Data: map[string]interface{}{
			"PID":        1,
			"machine":    "MAC",
			"resultList": sendList,
		},
	})
}

func upLoadImg() {
	img := makeImg()
	bodyBuf := &bytes.Buffer{}
	bodyWriter := multipart.NewWriter(bodyBuf)

	fileWriter, _ := bodyWriter.CreateFormFile("file", "img_"+strconv.FormatInt(int64(DID), 10)+".jpg")
	jpeg.Encode(fileWriter, img, &jpeg.Options{Quality: 90})
	contentType := bodyWriter.FormDataContentType()
	bodyWriter.Close()
	_, err := http.Post("http://"+Url.Host+"/upload", contentType, bodyBuf)
	if err != nil {
		log.Fatalln(err)
	}
	fmt.Println("Done")
	Done = true
}

func makeImg() *image.RGBA {
	width := 512
	height := 512
	upLeft := image.Point{}
	lowRight := image.Point{X: width, Y: height}
	sendList := make([]string, 0)
	if DOERR {
		if len(recvMedList) != 1 {
			sendList = append(sendList, recvMedList[0])
		}
	} else {
		sendList = recvMedList
	}
	img := image.NewRGBA(image.Rectangle{Min: upLeft, Max: lowRight})

	for i := range sendList {
		addLabel(img, 100, 100+10*(i+1), sendList[i])
	}
	return img
}

func addLabel(img *image.RGBA, x, y int, label string) {
	col := color.RGBA{200, 100, 0, 255}
	point := fixed.Point26_6{fixed.Int26_6(x * 128), fixed.Int26_6(y * 128)}

	d := &font.Drawer{
		Dst:  img,
		Src:  image.NewUniform(col),
		Face: basicfont.Face7x13,
		Dot:  point,
	}
	d.DrawString(label)
}

func ReadMsg(ws *websocket.Conn) {
	for {
		msg := make(map[string]interface{})
		ws.ReadJSON(&msg)
		fmt.Println("Recv:", msg)
		switch msg["function"] {
		case "getPrescription":
			if msg["status"].(bool) {
				for _, v := range msg["data"].(map[string]interface{})["medList"].([]interface{}) {
					recvMedList = append(recvMedList, v.(string))
				}
				go sendInfo()
			}
		case "detection":
			if msg["status"].(bool) {
				DID = msg["data"].(map[string]interface{})["DID"].(float64)
				go upLoadImg()
			}
		}
	}
}
