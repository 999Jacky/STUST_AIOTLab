package main

import (
	"encoding/json"
	"fmt"
	"github.com/gorilla/websocket"
)

const (
	JoinXav = iota
	JoinApp
	Waiting
	DetectionResult
	Ok
	BootComplete
)

const (
	GroupXav = iota
	GroupApp
)

var XavConn map[WsClient]bool
var AppConn map[WsClient]bool

func init() {
	XavConn = make(map[WsClient]bool, 0)
	AppConn = make(map[WsClient]bool, 0)
}

type WsClient struct {
	Wsconn *websocket.Conn
	Group  int
}

type commStruct struct {
	Status   int    `json:"status"`
	Qr       string `json:"qr"`
	Cam      []Med  `json:"cam"`
	ImgUrl string `json:"img_url"`
}
type Med struct {
	Mid   string `json:"mid"`
	Count int    `json:"count"`
}

func test() {
	meds := Med{
		Mid:   "123",
		Count: 20,
	}
	m := commStruct{
		Status: DetectionResult,
		Qr:     "abc123",
		Cam:    []Med{meds, meds, meds},
	}
	j, _ := json.Marshal(m)
	fmt.Println(string(j))
}
