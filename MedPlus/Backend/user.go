package main

import (
)

// Patient 病人看病
func Patient(data map[string]interface{}, wsConn *WsConnStruct) {
	if !CheckMapKeyIsExist(data, "name", "patientsID") {
		wsConn.WriteMissKey("patient")
		return
	}
	personalID := data["patientsID"].(string)
	name := data["name"].(string)
	err := AddPatients(personalID, name)
	if err != nil {
		wsConn.WriteJson("patient", false, nil)
		Log.Errorln(err)
	}
	wsConn.WriteJson("patient", true, nil)
}

// GetPatient  查病人姓名
func GetPatient(data map[string]interface{}, wsConn *WsConnStruct) {
	if !CheckMapKeyIsExist(data, "patientsID") {
		wsConn.WriteMissKey("getpatient")
		return
	}
	personalID := data["patientsID"].(string)
	name := GetPatientName(personalID)
	if name != "" {
		wsConn.WriteJson("getPatient", true, &PatientInfoStruct{
			Name:       name,
			PatientsID: personalID,
		})
	} else {
		wsConn.WriteJson("getPatient", false, nil)
	}
}

// DocRegistered 醫護註冊
func DocRegistered(data map[string]interface{}, wsConn *WsConnStruct) {
	if !CheckMapKeyIsExist(data, "name", "job_code", "passwd") {
		wsConn.WriteMissKey("registered")
		return
	}
	docName := data["name"].(string)
	jobCode := data["job_code"].(string)
	passWd := data["passwd"].(string)
	err := AddDocAccount(docName, jobCode, passWd)
	if err != nil {
		wsConn.WriteJson("registered", false, nil)
	} else {
		wsConn.WriteJson("registered", true, nil)
	}
}

// DocLogin 醫護登入
func DocLogin(data map[string]interface{}, wsConn *WsConnStruct) {
	if !CheckMapKeyIsExist(data, "name", "passwd") {
		wsConn.WriteMissKey("login")
		return
	}
	docName := data["name"].(string)
	pass := data["passwd"].(string)
	docInfo, err := GetDocInfo(docName, pass)
	if err != nil {
		Log.Errorln(err)
		wsConn.WriteJson("login", false, nil)
		return
	}

	wsConn.Locker.Lock()
	wsConn.DocInfo = docInfo
	wsConn.ConnType = Web
	wsConn.Locker.Unlock()

	WebConnLock.Lock()
	WebConn[docInfo.Name] = wsConn
	WebConnLock.Unlock()
	wsConn.WriteJson("login", true, docInfo)
}
