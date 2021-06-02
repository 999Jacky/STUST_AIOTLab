package main

import (
	"crypto/md5"
	"encoding/json"
	"fmt"
	"github.com/gorilla/websocket"
	"net"
	"net/http"
	"net/url"
	"strconv"
	"time"
)

var BackendServerIP = ""
var BoxMd5Mac = ""
var DebugBool = false

func ConnectBackendServer() {
	Log.Debugln("Connecting Backend Server")
	u := url.URL{Scheme: "ws", Host: BackendServerIP, Path: "/ws"}
	c, _, err := websocket.DefaultDialer.Dial(u.String(), nil)
	if err != nil {
		Log.Error(err)
		time.Sleep(1 * time.Second)
		go ConnectBackendServer()
		return
	}
	BackendServer.Conn = c
	Log.Infoln("Success to Connect Backend Server")
	for {
		Log.Infoln("確認辨識機器連線")
		_, err = http.Get("http://" + DetectionServerIP + "/check")
		if err == nil {
			Log.Infoln("辨識機器連線成功")
			break
		}
		time.Sleep(1 * time.Second)
	}
	LoginBackendServer()
	if DebugBool {
		DebegFunc()
	}

	go BackendServerMsgReader()
}

func DebegFunc() {
	go func() {
		if DebugBool {
			time.Sleep(5 * time.Second)
			// BackendServer.WriteJSON(BackendWsMsg{
			// 	Function: "login",
			// 	Data: map[string]interface{}{
			// 		"name":   "張三",
			// 		"passwd": "abc123",
			// 	},
			// })
			// BackendServer.WriteJSON(BackendWsMsg{
			// 	Function: "select",
			// 	Data: map[string]interface{}{
			// 		"machine": BoxMd5Mac,
			// 	},
			// })
			// LoginBackendServer()
			WriteJson2Backend(BackendWsMsg{
				Function: "login",
				Data: map[string]interface{}{
					"name":   "張三",
					"passwd": fmt.Sprintf("%x", md5.Sum([]byte("abc123"))),
				},
			})
			WriteJson2Backend(BackendWsMsg{
				Function: "select",
				Data: map[string]interface{}{
					"machine": BoxMd5Mac,
				},
			})
		}
	}()
}

func LoginBackendServer() {
	if len(BoxMd5Mac) == 0 {
		mac := getMacAddr()
		if len(mac) == 0 {
			Log.Error("Can't get Mac address")
			mac = "abc123"
		}
		data := []byte(mac)
		macMd5 := md5.Sum(data)
		m := fmt.Sprintf("%x", macMd5)
		Log.Debugln("mac: ", string(data), "macMd5: ", m)
		BoxMd5Mac = m
	}
	Log.Debugln("Login to Backend")

	// err := BackendServer.WriteJSON(BackendWsMsg{
	// 	Function: LoginBackendServerCMD,
	// 	Data: map[string]interface{}{
	// 		"machineID": BoxMd5Mac,
	// 	},
	// })
	// if err != nil {
	//		Log.Fatalln(err)
	//	}
	WriteJson2Backend(BackendWsMsg{
		Function: LoginBackendServerCMD,
		Data: map[string]interface{}{
			"machineID": BoxMd5Mac,
		},
	})

}

func BackendServerMsgReader() {
	for {
		_, message, err := BackendServer.Conn.ReadMessage()
		if err != nil {
			Log.Errorln(err)
			Log.Debugln("Reconnecting Backend Server in 1s")
			_ = BackendServer.Conn.Close()
			time.Sleep(1 * time.Second)
			go ConnectBackendServer()
			break
		}
		Log.Debugln(string(message))
		deJsonMsg := BackendWsMsg{}
		err = json.Unmarshal(message, &deJsonMsg)
		if err != nil {
			Log.Errorln(err)
		}
		if deJsonMsg.Status {
			// TODO: ADD action , TRY Catch
			switch deJsonMsg.Function {
			case GetMedInfoCMD:
				MedsInfo = make(map[string]bool)
				for _, v := range deJsonMsg.Data["medList"].([]interface{}) {
					MedsInfo[v.(string)] = true
				}
			case DetectionDoneCMD:
				Did = int(deJsonMsg.Data["DID"].(float64))
			case DisconnectCMD:
				// BackendServer.Conn.Close()
			}
		} else {
			Log.Errorln(deJsonMsg)
		}
	}
}

func GetMedsList(pid string) {
	pidInt, err := strconv.Atoi(pid)
	Pid = pidInt
	if err != nil {
		Log.Errorln(err)
		return
	}
	WriteJson2Backend(BackendWsMsg{
		Function: GetMedInfoCMD,
		Data: map[string]interface{}{
			"PID": pidInt,
		},
	})
}

func getMacAddrs() (macAddrs []string) {
	netInterfaces, err := net.Interfaces()
	if err != nil {
		fmt.Printf("fail to get net interfaces: %v", err)
		return macAddrs
	}

	for _, netInterface := range netInterfaces {
		macAddr := netInterface.HardwareAddr.String()
		if len(macAddr) == 0 {
			continue
		}

		macAddrs = append(macAddrs, macAddr)
	}
	return macAddrs
}

func getMacAddr() string {
	netInterfaces, err := net.Interfaces()
	if err != nil {
		fmt.Printf("fail to get net interfaces: %v", err)
		return ""
	}

	for _, netInterface := range netInterfaces {
		macAddr := netInterface.HardwareAddr.String()
		if len(macAddr) == 0 {
			continue
		}

		return macAddr
	}
	return ""
}
