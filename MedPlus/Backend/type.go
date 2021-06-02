package main

import (
	"github.com/gorilla/websocket"
	"sync"
)

type WsMsg struct {
	Function string      `json:"function"`
	Status   bool        `json:"status"`
	Data     interface{} `json:"data"`
}

const (
	Web = iota
	Box
)
const (
	// SickRoom 病房
	SickRoom = iota
	// Outpatient 門診
	Outpatient
)

type WsConnStruct struct {
	Conn   *websocket.Conn
	Locker sync.Mutex
	// ConnType 0:Web 1:box
	ConnType int

	IsLogin bool
	DocInfo DocInfoStruct

	BoxMac  string
	IsUsing bool

	BindingConn *WsConnStruct
}
type DocInfoStruct struct {
	StafesID int `json:"stafesID"`
	// JobCode
	// 醫生	D
	// 護士	N
	// 藥劑師P
	JobCode string `json:"job_code"`
	Name    string `json:"name"`
}

type MaineListStruct struct {
	MachineList []MachineListDataStruct `json:"machineList"`
}

type MachineListDataStruct struct {
	MachineID string `json:"machineID"`
	Using     bool   `json:"using"`
}

type PrescriptionInfoStruct struct {
	PersonalID string   `json:"patientsID"`
	StafesID   int      `json:"stafesID"`
	Type       string   `json:"type"`
	MedList    []string `json:"medList"`
}

type ResultListStruct struct {
	DID     float64
	MedCode string
}

type MkupPrescriptionListStruct struct {
	PID     float64
	MedCode string
}

type WebResultStruct struct {
	Resultdata []WebResultDataStruct `json:"resultdata"`
}

type WebResultDataStruct struct {
	Equals      bool     `json:"equals"`
	DID         float64  `json:"DID"`
	PID         float64  `json:"PID"`
	// MachineType MedEye or MedPlus
	MachineType string   `json:"machineType"`
	TargetList  []string `json:"targetList"`
	ResultList  []string `json:"resultList"`
}

type PatientInfoStruct struct {
	Name       string `json:"name"`
	PatientsID string `json:"patientsID"`
}
