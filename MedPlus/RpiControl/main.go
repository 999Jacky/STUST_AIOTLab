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
	"time"
)

var Log *logrus.Logger
var VER = "1.0"
var DetectionServerIP string

var upgrader = websocket.Upgrader{CheckOrigin: func(r *http.Request) bool {
	return true
}}

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

func main() {
	Log.Println("Ver:", VER)
	flag.StringVar(&DetectionServerIP, "DIP", "127.0.0.1:5000", "DetectionServerIP")
	flag.StringVar(&BackendServerIP, "BIP", "127.0.0.1:3000", "Backend Server Ip")
	flag.StringVar(&BarcodeDev, "b", "COM7", "Barcode Com")
	bootDelay := flag.Int("bootDelay", 0, "啟動延時(s)")
	flag.Parse()
	Log.Info("Delay ", *bootDelay, "s")
	time.Sleep(time.Duration(*bootDelay) * time.Second)
	ConnectBackendServer()
	go BarcodeInit()
	router := gin.New()
	router.Use(ginlogrus.Logger(Log), gin.Recovery())
	router.GET("/ws", func(c *gin.Context) {
		wsConn, err := upgrader.Upgrade(c.Writer, c.Request, nil)
		if err != nil {
			Log.Errorln("upgrade:", err)
			return
		}
		DetectionBox.Conn = wsConn
		defer func() {
			_ = wsConn.Close()
		}()
		for {
			data := make(map[string]interface{})
			err := wsConn.ReadJSON(&data)
			if err != nil {
				Log.Errorln("read:", err)
				break
			}
			RecvMsg(data)
		}
	})
	server := &http.Server{
		Addr:    ":3001",
		Handler: router,
	}

	quit := make(chan os.Signal)
	signal.Notify(quit, os.Interrupt)

	go func() {
		<-quit
		Log.Println("receive interrupt signal")
		if err := server.Close(); err != nil {
			Log.Fatal("Server Close:", err)
		}
	}()
	Log.Infoln("Ws Server running ", "ip:", server.Addr)
	if err := server.ListenAndServe(); err != nil {
		if err == http.ErrServerClosed {
			Log.Println("Server closed under request")
		} else {
			Log.Fatal("Server closed unexpect")
		}
	}

	Log.Infoln("Server quit")
}
