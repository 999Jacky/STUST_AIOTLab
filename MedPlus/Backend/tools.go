package main

import (
	"crypto/md5"
	"encoding/hex"
	"encoding/json"
)

var WorkingDir string
var DebugFlag bool

func CheckMapKeyIsExist(data map[string]interface{}, key ...string) bool {
	for _, v := range key {
		if _, ok := data[v]; !ok {
			return false
		}
	}
	return true
}

func Md5(s string) string {
	m := md5.Sum([]byte (s))
	return hex.EncodeToString(m[:])
}

func (ws *WsConnStruct) WriteJson(function string, status bool, data interface{}) {
	ws.Locker.Lock()
	defer ws.Locker.Unlock()
	if DebugFlag {
		d, _ := json.Marshal(&WsMsg{
			Function: function,
			Status:   status,
			Data:     data,
		})
		Log.Debugln("Send:", string(d))
	}
	err := ws.Conn.WriteJSON(&WsMsg{
		Function: function,
		Status:   status,
		Data:     data,
	})
	if err != nil {
		Log.Errorln(err)
	}
}

func (ws *WsConnStruct) WriteJson2Binding(function string, status bool, data interface{}) {
	if ws == nil || ws.BindingConn == nil {
		Log.Errorln("Send msg 2 nil")
		return
	}
	ws.BindingConn.Locker.Lock()
	defer ws.BindingConn.Locker.Unlock()
	if DebugFlag {
		d, _ := json.Marshal(&WsMsg{
			Function: function,
			Status:   status,
			Data:     data,
		})
		Log.Debugln("Send2Binding:", string(d))
	}
	err := ws.BindingConn.Conn.WriteJSON(&WsMsg{
		Function: function,
		Status:   status,
		Data:     data,
	})
	if err != nil {
		Log.Errorln(err)
	}

}

func (ws *WsConnStruct) WriteMissKey(function string) {
	ws.WriteJson(function, false, map[string]string{
		"msg": "缺少key",
	})
}
