package main

import (
	"flag"
	"fmt"
	"github.com/gin-gonic/gin"
	"github.com/gorilla/websocket"
	"github.com/mattn/go-colorable"
	"github.com/sirupsen/logrus"
	ginlogrus "github.com/toorop/gin-logrus"
	"net/http"
	"os"
	"os/signal"
	"path"
	"runtime"
)

var Version = "1.1"

var upgrader = websocket.Upgrader{CheckOrigin: func(r *http.Request) bool {
	return true
}}

var ServerIP = ""
var ServerPort = ""
var Log *logrus.Logger

func init() {
	Log = logrus.New()
	Log.SetOutput(os.Stdout)
	Log.SetLevel(logrus.DebugLevel)
	Log.SetFormatter(&logrus.TextFormatter{ForceColors: true,
		DisableLevelTruncation: true, PadLevelText: true,
		TimestampFormat: "2006-01-02 15:04:05", FullTimestamp: true,
		CallerPrettyfier: func(f *runtime.Frame) (string, string) {
			filename := path.Base(f.File)
			return fmt.Sprintf("%s()", f.Function), fmt.Sprintf("%s:%d", filename, f.Line)
		}})

	if runtime.GOOS == "windows" {
		Log.SetOutput(colorable.NewColorableStdout())
	}
	Log.SetReportCaller(true)
}

/*
察看還沒完成!!!
*/
func main() {
	flag.BoolVar(&DebugFlag, "d", false, "DebugFlag")
	flag.StringVar(&ServerIP, "ip", "", "ServerIP")
	flag.StringVar(&ServerPort, "p", "3000", "ServerPort")
	flag.BoolVar(&UsingFakeDB, "FakeDB", false, "Use FakeDB")
	flag.Parse()
	Log.Infoln("Ver：" + Version)
	p, err := os.Getwd()
	if err != nil {
		Log.Errorln("取得工作目錄失敗")
		os.Exit(1)
	}
	WorkingDir = p
	Log.Infoln("WorkingDir:", p)
	_ = os.Mkdir(path.Join(WorkingDir, "img"), 0777)
	go ConnectDB()
	router := gin.New()
	router.Use(ginlogrus.Logger(Log), gin.Recovery())
	router.GET("/ws", func(c *gin.Context) {
		wsConn, err := upgrader.Upgrade(c.Writer, c.Request, nil)
		if err != nil {
			Log.Errorln("upgrade:", err)
			return
		}
		wcs := &WsConnStruct{
			Conn:        wsConn,
			ConnType:    -1,
			BindingConn: nil,
		}
		for {
			data := make(map[string]interface{})
			err := wsConn.ReadJSON(&data)
			if DebugFlag {
				Log.Debugln("recv Msg:", data)
			}
			if err != nil {
				Log.Errorln("read:", err)
				wcs.Locker.Lock()
				if wcs.BindingConn != nil {
					wcs.BindingConn.Locker.Lock()
					wcs.BindingConn.IsUsing = false
					wcs.BindingConn.BindingConn = nil
					wcs.BindingConn.Locker.Unlock()
				}
				switch wcs.ConnType {
				case Box:
					BoxConnLock.Lock()
					delete(BoxConn, wcs.BoxMac)
					BoxConnLock.Unlock()
				case Web:
					WebConnLock.Lock()
					delete(WebConn, wcs.DocInfo.Name)
					WebConnLock.Unlock()
				default:

				}
				wcs.Locker.Unlock()
				break
			}
			RecvMsg(data, wcs)
		}
	})
	router.POST("/upload", func(c *gin.Context) {
		// 上傳圖片
		file, err := c.FormFile("file")
		if err != nil {
			Log.Errorln(err)
			return
		}
		if err := c.SaveUploadedFile(file, path.Join(WorkingDir, "img", file.Filename)); err != nil {
			Log.Errorln(err)
			return
		}
		go ReceiveImgAndPushMsg(file.Filename)
	})

	// 下載圖片
	router.StaticFS("/download", http.Dir(path.Join(WorkingDir, "img")))

	server := &http.Server{
		Addr:    ServerIP + ":" + ServerPort,
		Handler: router,
	}

	quit := make(chan os.Signal)
	signal.Notify(quit, os.Interrupt)

	go func() {
		<-quit
		Log.Infoln("receive interrupt signal")
		if err := server.Close(); err != nil {
			Log.Errorln("Server Close:", err)
			os.Exit(1)
		}
	}()
	Log.Infoln("Server running ", "ip:", server.Addr)
	if err := server.ListenAndServe(); err != nil {
		if err == http.ErrServerClosed {
			Log.Infoln("Server closed under request")
		} else {
			Log.Errorln("Server closed unexpect")
			os.Exit(1)
		}
	}

	Log.Infoln("Server quit")
}

func RecvMsg(data map[string]interface{}, wsConn *WsConnStruct) {
	switch data["function"] {
	case "patient":
		// 病人看病
		Patient(data["data"].(map[string]interface{}), wsConn)
	case "getPatient":
		// 查病人姓名
		GetPatient(data["data"].(map[string]interface{}), wsConn)
	case "registered":
		// 醫護註冊
		DocRegistered(data["data"].(map[string]interface{}), wsConn)
	case "login":
		// 醫護登入
		DocLogin(data["data"].(map[string]interface{}), wsConn)
	case "machine":
		// 機器登入
		MachineLogin(data["data"].(map[string]interface{}), wsConn)
	case "machineList":
		// 取得機器清單
		GetMachineList(wsConn)
	case "select":
		// 選擇機器
		SelectBox(data["data"].(map[string]interface{}), wsConn)
	case "prescription":
		// 開藥
		// 用API Set
	case "getPrescription":
		// 取得藥單
		GetPrescription(data["data"].(map[string]interface{}), wsConn)
	case "detection":
		// 辨識
		// 辨識完傳result格式給UI
		Detection(data["data"].(map[string]interface{}), wsConn)
	case "result":
		// 查看
		GetDetectionResult(data["data"].(map[string]interface{}), wsConn)
	case "disconnect":
	// 斷線

	// case "receiveImg":
	// server接收到圖片
	// ReceiveImg(data, wsConn)
	default:
		switch data["status"].(float64) {
		case 5:
			// 開機完成
		case 3:
			// 舊機台資料
			RecvMedEyeData(data)
		}

	}

}
