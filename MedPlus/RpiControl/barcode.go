package main

import (
	"go.bug.st/serial"
	"time"
)

var BarcodeDev string

func BarcodeDevReconnect() {
	Log.Errorln("Barcode Disconnected reconnect in 1s")
	time.Sleep(1 * time.Second)
	go BarcodeInit()
}

func BarcodeInit() {
	Log.Debugln("Connecting Barcode Dev")
	port, err := serial.Open(BarcodeDev, &serial.Mode{BaudRate: 115200})
	if err != nil {
		Log.Errorln(err)
		BarcodeDevReconnect()
		return
	}
	Log.Infoln("Waiting Barcode Input")
	BarcodeReader(port)
}

func BarcodeReader(port serial.Port) {
	buff := make([]byte, 100)
	for {
		n, err := port.Read(buff)
		if err != nil {
			Log.Println(err)
			_ = port.Close()
			go BarcodeDevReconnect()
			return
		}
		Log.Debugln("Barcode Input: ", string(buff[:n]))
		Did = -1
		Pid = -1
		go GetMedsList(string(buff[:n]))
		SendCtl = true
	}

}
