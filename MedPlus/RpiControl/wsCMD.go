package main

import (
	"github.com/gorilla/websocket"
	"sync"
)

var BackendServer *ConnectStruct
var DetectionBox *ConnectStruct

func init() {
	BackendServer = &ConnectStruct{}
	DetectionBox = &ConnectStruct{}
}

var (
	GetMedInfoCMD         = "getPrescription"
	DetectionDoneCMD      = "detection"
	DisconnectCMD         = "disconnect"
	RespRecvImgCMD        = "receiveImg"
	LoginBackendServerCMD = "machine"
)

type ConnectStruct struct {
	MuLock sync.Mutex
	Conn   *websocket.Conn
}

type BackendWsMsg struct {
	Function string                 `json:"function"`
	Data     map[string]interface{} `json:"data,omitempty"`
	Status   bool                   `json:"status,omitempty"`
}

func WriteJson2Backend(msg BackendWsMsg) {
	if BackendServer.Conn == nil {
		return
	}
	BackendServer.MuLock.Lock()
	defer BackendServer.MuLock.Unlock()
	err := BackendServer.Conn.WriteJSON(msg)
	if err != nil {
		Log.Errorln(err)
		_ = BackendServer.Conn.Close()
	}
}

func WriteJson2DetectionBox(msg BackendWsMsg) {
	if DetectionBox.Conn == nil {
		return
	}
	DetectionBox.MuLock.Lock()
	defer DetectionBox.MuLock.Unlock()
	err := DetectionBox.Conn.WriteJSON(msg)
	if err != nil {
		Log.Errorln(err)
		_ = DetectionBox.Conn.Close()
	}

}
