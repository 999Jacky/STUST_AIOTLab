package main

import (
	"sync"
)

var BoxConn map[string]*WsConnStruct // BoxConn 辨識設備
var BoxConnLock sync.RWMutex

func init() {
	BoxConn = make(map[string]*WsConnStruct)
}

// MachineLogin 機器登入
func MachineLogin(data map[string]interface{}, wsConn *WsConnStruct) {
	if !CheckMapKeyIsExist(data, "machineID") {
		wsConn.WriteMissKey("machine")
		return
	}
	mac := data["machineID"].(string)
	wsConn.Locker.Lock()
	wsConn.ConnType = Box
	wsConn.BoxMac = mac
	wsConn.IsUsing = false
	wsConn.Locker.Unlock()

	BoxConnLock.Lock()
	BoxConn[mac] = wsConn
	BoxConnLock.Unlock()

	wsConn.WriteJson("machine", true, nil)
}

// GetMachineList 取得機器清單
func GetMachineList(wsConn *WsConnStruct) {
	machineList := make([]MachineListDataStruct, 0)
	BoxConnLock.RLock()
	for i := range BoxConn {
		machineList = append(machineList, MachineListDataStruct{
			MachineID: i,
			Using:     BoxConn[i].IsUsing,
		})
	}
	BoxConnLock.RUnlock()
	wsConn.WriteJson("machineList", true, &MaineListStruct{
		machineList,
	})
}

// SelectBox 選擇機器
func SelectBox(data map[string]interface{}, wsConn *WsConnStruct) {
	if !CheckMapKeyIsExist(data, "machine") {
		wsConn.WriteMissKey("select")
		return
	}
	mac := data["machine"].(string)
	BoxConnLock.Lock()
	boxConn, ok := BoxConn[mac]
	if !ok {
		wsConn.WriteJson("select", false, map[string]string{
			"msg": "機器不存在",
		})
		BoxConnLock.Unlock()
		return
	}
	if boxConn.IsUsing {
		wsConn.WriteJson("select", false, map[string]string{
			"msg": "機器使用中",
		})
		BoxConnLock.Unlock()
		return
	}
	boxConn.IsUsing = true
	BoxConnLock.Unlock()

	wsConn.Locker.Lock()
	wsConn.BindingConn = boxConn
	wsConn.Locker.Unlock()
	boxConn.Locker.Lock()
	boxConn.BindingConn = wsConn
	boxConn.Locker.Unlock()
	wsConn.WriteJson("select", true, nil)
}

// Detection 辨識
func Detection(data map[string]interface{}, wsConn *WsConnStruct) {
	if !CheckMapKeyIsExist(data, "PID", "machine", "resultList") {
		wsConn.WriteMissKey("detection")
		return
	}
	pid := data["PID"].(float64)
	machineMac := data["machine"].(string)
	resultList := make([]string, 0)
	for _, v := range data["resultList"].([]interface{}) {
		resultList = append(resultList, v.(string))
	}
	pi := GetPatientsInfoFromPID(pid)
	ml, err := GetPrescriptionMedsInfo(pid)
	if err != nil {
		Log.Errorln(err)
		return
	}
	pi.MedList = ml
	did, err := SetDetectionInfo(pid, pi.StafesID, machineMac)
	for _, v := range resultList {
		err := SetResult(did, v)
		if err != nil {
			Log.Errorln(err)
		}
	}
	if err != nil {
		Log.Errorln(err)
		wsConn.WriteJson("detection", false, nil)
		return
	}
	wsConn.WriteJson("detection", true, map[string]interface{}{
		"DID": did,
	})
	info := WebResultStruct{Resultdata: []WebResultDataStruct{{
		Equals:      CheckMedsEquals(pi.MedList, resultList),
		DID:         did,
		PID:         pid,
		MachineType: "MedPlus",
		TargetList:  pi.MedList,
		ResultList:  resultList,
	}}}
	wsConn.WriteJson2Binding("result", true, info)
}
