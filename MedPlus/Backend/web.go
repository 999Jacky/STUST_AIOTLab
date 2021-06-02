package main

import (
	"strings"
	"sync"
	"time"
)

var WebConn map[string]*WsConnStruct // WebConn 雲端平台
var WebConnLock sync.RWMutex

func init() {
	WebConn = make(map[string]*WsConnStruct)
}

// GetPrescription 取得藥單
func GetPrescription(data map[string]interface{}, wsConn *WsConnStruct) {
	if !CheckMapKeyIsExist(data, "PID") {
		wsConn.WriteMissKey("getPrescription")
		return
	}
	pid := data["PID"].(float64)
	PtInfo := GetPatientsInfoFromPID(pid)
	var err error
	PtInfo.MedList, err = GetPrescriptionMedsInfo(pid)
	if err != nil {
		Log.Errorln(err)
		wsConn.WriteJson("getPrescription", false, nil)
		return
	}
	wsConn.WriteJson("getPrescription", true, PtInfo)
	wsConn.WriteJson2Binding("getPrescription", true, PtInfo)
}

// GetDetectionResult 查看
func GetDetectionResult(data map[string]interface{}, wsConn *WsConnStruct) {
	// TODO: Not Finish
	if !CheckMapKeyIsExist(data, "period", "med") {
		wsConn.WriteMissKey("result")
		return
	}
	period := data["period"].(string)
	// med := data["med"].(string)
	timeStart := ""
	timeEnd := ""
	if period != "all" {
		tmp := strings.Split(period, "｜")
		timeStart = tmp[0]
		timeEnd = tmp[1]
	}

	pids, dids, machineType, err := GetPrescriptionInfosFromTime(timeStart, timeEnd)
	if err != nil {
		Log.Errorln(err)
		wsConn.WriteJson("result", false, nil)
		return
	}
	mkupList, err := GetMkupPrescritptionFromPid(pids)
	if err != nil {
		Log.Errorln(err)
		wsConn.WriteJson("result", false, nil)
		return
	}
	resultList, err := GetResultFromDid(dids)
	if err != nil {
		Log.Errorln(err)
		wsConn.WriteJson("result", false, nil)
		return
	}
	mkupMap := mkupList2Map(mkupList)
	resultMap := resultList2Map(resultList)
	info := WebResultStruct{}
	for i := range pids {
		info.Resultdata = append(info.Resultdata, WebResultDataStruct{
			Equals:      CheckMedsEquals(mkupMap[pids[i]], resultMap[dids[i]]),
			DID:         dids[i],
			PID:         pids[i],
			MachineType: machineType[i],
			TargetList:  mkupMap[pids[i]],
			ResultList:  resultMap[dids[i]],
		})
	}
	wsConn.WriteJson("result", true, info)
}

func CheckMedsEquals(Target []string, Result []string) bool {
	if len(Target) != len(Result) {
		return false
	}
	for _, v := range Target {
		found := false
		for _, vv := range Result {
			if v == vv {
				found = true
				break
			}
		}
		if !found {
			return false
		}
	}
	return true
}

func mkupList2Map(l []MkupPrescriptionListStruct) map[float64][]string {
	m := make(map[float64][]string)
	for _, v := range l {
		if value, ok := m[v.PID]; ok {
			value = append(value, v.MedCode)
			m[v.PID] = value
		} else {
			t := make([]string, 0)
			t = append(t, v.MedCode)
			m[v.PID] = t
		}
	}
	return m
}
func resultList2Map(l []ResultListStruct) map[float64][]string {
	m := make(map[float64][]string)
	for _, v := range l {
		if value, ok := m[v.DID]; ok {
			value = append(value, v.MedCode)
			m[v.DID] = value
		} else {
			t := make([]string, 0)
			t = append(t, v.MedCode)
			m[v.DID] = t
		}
	}
	return m
}

// ReceiveImgAndPushMsg   server接收到圖片
func ReceiveImgAndPushMsg(fileName string) {
	n1 := strings.Index(fileName, "_")
	n2 := strings.Index(fileName, ".")
	did := fileName[n1+1 : n2]
	machineMac := ""
	for machineMac == "" {
		machineMac = GetMachineMacFormDID(did)
		time.Sleep(300 * time.Millisecond)
	}
	BoxConnLock.RLock()
	wsBOXConn := BoxConn[machineMac]
	BoxConnLock.RUnlock()
	wsBOXConn.WriteJson2Binding("receiveImg", true, nil)
}
