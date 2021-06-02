package main

import (
	"flag"
	"fmt"
	"github.com/gin-gonic/gin"
	"github.com/gorilla/websocket"
	"log"
	"net/http"
	"net/url"
	"os"
	"os/exec"
	"os/signal"
	"sync"
	"time"
)

var Ver = "1.10"
var upgrader = websocket.Upgrader{CheckOrigin: func(r *http.Request) bool {
	return true
}}
var send = true
var bootCompleteBool = false
var mutxLock sync.Mutex

var RemoteWS *websocket.Conn
var Send2Remote bool

func Connect2RemoteServer(ip string) {
	c, _, err := websocket.DefaultDialer.Dial(ip, nil)
	if err != nil {
		fmt.Println(err)
		time.Sleep(1 * time.Second)
		go Connect2RemoteServer(ip)
		return
	}
	fmt.Println("success connect to remote")
	go func() {
		for {
			data := make(map[string]interface{})
			err := RemoteWS.ReadJSON(&data)
			if err != nil {
				RemoteWS.Close()
				go Connect2RemoteServer(ip)
				return
			}
		}
	}()
	RemoteWS = c
	Send2Remote = true
}

func main() {
	log.Println("Ver:", Ver)
	imgDir := flag.String("imgDir", "/home/nvidia/img", "ImgDir")
	dbJar := flag.String("dbJar", "", "dbJarPath")
	ip := flag.String("ip", "192.168.10.1:3000", "ImgIP")
	remoteIp := flag.String("remoteIp", "", "新後端IP")
	flag.Parse()
	router := gin.Default()
	router.GET("/ws", func(c *gin.Context) {
		wsConn, err := upgrader.Upgrade(c.Writer, c.Request, nil)
		if err != nil {
			log.Println("upgrade:", err)
			return
		}
		client := &WsClient{Group: -1}
		defer func() {
			_ = wsConn.Close()
			mutxLock.Lock()
			switch client.Group {
			case GroupXav:
				bootCompleteBool = false
				delete(XavConn, *client)
			case GroupApp:
				delete(AppConn, *client)
			default:
				break
			}
			mutxLock.Unlock()
		}()
		for {
			data := make(map[string]interface{})
			err := wsConn.ReadJSON(&data)
			if err != nil {
				log.Println("read:", err)
				break
			}

			if v, ok := data["status"]; ok {
				switch int(v.(float64)) {
				case JoinXav:
					send = true
					client = &WsClient{
						Wsconn: wsConn,
						Group:  GroupXav,
					}
					mutxLock.Lock()
					XavConn[*client] = true
					mutxLock.Unlock()
					keepAlive(*client, time.Second*3)
					wserr := wsConn.WriteJSON(map[string]interface{}{
						"status": Ok,
					})
					if wserr != nil {
						return
					}
				case JoinApp:
					send = true
					client = &WsClient{
						Wsconn: wsConn,
						Group:  GroupApp,
					}
					mutxLock.Lock()
					AppConn[*client] = true
					mutxLock.Unlock()
					keepAlive(*client, time.Second*3)
					if !bootCompleteBool {
						// V1.8 針對月月網頁處理
						wserr := wsConn.WriteJSON(map[string]interface{}{
							"status": Ok,
						})
						if wserr != nil {
							return
						}
					}
				case Waiting:
					log.Println("received Waiting")
					send = true
				case BootComplete:
					log.Println("received BootComplete")
					bootCompleteBool = true
					WsBroadcast(AppConn, map[string]interface{}{
						"status": Ok,
					})

				default:
					switch client.Group {
					case GroupXav:
						if send {
							send = false
							data["qr"] = getCode(fmt.Sprintf("%v", data["qr"]))
							// data["img_url"] = "http://192.168.10.1:3000/img/" + data["img_url"].(string) + ".jpg"
							data["img_url"] = "http://" + *ip + "/img/" + data["img_url"].(string) + ".jpg"
							WsBroadcast(AppConn, data)
							if Send2Remote {
								err := RemoteWS.WriteJSON(data)
								if err != nil {
									Send2Remote = false
									RemoteWS.Close()
									u := url.URL{Scheme: "ws", Host: *remoteIp, Path: "/ws"}
									Connect2RemoteServer(u.String())
								}
							}
						} else {
							log.Println("msg Dropped")
						}
					case GroupApp:
						WsBroadcast(XavConn, data)
					default:
						return
					}
				}
			}
		}
	})

	router.Static("/img", *imgDir)

	router.GET("/stat", func(c *gin.Context) {
		if bootCompleteBool {
			c.String(200, "true")
		} else {
			c.String(200, "false")
		}

	})

	router.GET("/cmd/shutdown", func(c *gin.Context) {
		_ = exec.Command("/bin/bash", "-c", "sudo poweroff").Start()
	})

	router.GET("/cmd/reboot", func(c *gin.Context) {
		_ = exec.Command("/bin/bash", "-c", "sudo reboot").Start()
	})

	server := &http.Server{
		Addr:    ":3000",
		Handler: router,
	}

	go func() {
		dbJarPath := "/home/xavier/train_dummies_med/code/DBJar.jar"
		// call java db
		if *dbJar != "" {
			dbJarPath = *dbJar
		}
		err := exec.Command("/bin/bash", "-c", "java -jar "+dbJarPath).Start()
		if err != nil {
			fmt.Println(err)
		}
	}()

	if *remoteIp != "" {
		u := url.URL{Scheme: "ws", Host: *remoteIp, Path: "/ws"}
		go Connect2RemoteServer(u.String())
	}

	quit := make(chan os.Signal)
	signal.Notify(quit, os.Interrupt)

	go func() {
		<-quit
		log.Println("receive interrupt signal")
		if err := server.Close(); err != nil {
			log.Fatal("Server Close:", err)
		}
	}()
	fmt.Println("Server running ", "ip:", server.Addr)
	if err := server.ListenAndServe(); err != nil {
		if err == http.ErrServerClosed {
			log.Println("Server closed under request")
		} else {
			log.Println(err)
			log.Fatal("Server closed unexpect")
		}
	}

	log.Println("Server exiting")
}

func WsBroadcast(dst map[WsClient]bool, data map[string]interface{}) {
	mutxLock.Lock()
	for i := range dst {
		err := i.Wsconn.WriteJSON(data)
		if err != nil {
			switch i.Group {
			case GroupXav:
				bootCompleteBool = false
				delete(XavConn, i)
			case GroupApp:
				delete(AppConn, i)
			}
		}
	}
	mutxLock.Unlock()
	// fmt.Println("Xav:", len(XavConn))
	// fmt.Println("App:", len(AppConn))
}

func keepAlive(c WsClient, timeout time.Duration) {
	return
	// lastResponse := time.Now()
	// c.Wsconn.SetPongHandler(func(msg string) error {
	// 	lastResponse = time.Now()
	// 	return nil
	// })
	//
	// go func() {
	// 	for {
	// 		err := c.Wsconn.WriteControl(websocket.PingMessage, []byte("keepalive"), time.Now().Add(timeout))
	// 		if err != nil {
	// 			return
	// 		}
	// 		time.Sleep(timeout / 2)
	// 		if time.Now().Sub(lastResponse) > timeout {
	// 			switch c.Group {
	// 			case GroupXav:
	// 				delete(XavConn, c)
	// 			case GroupApp:
	// 				delete(AppConn, c)
	// 			}
	// 			c.Wsconn.Close()
	// 			return
	// 		}
	// 	}
	// }()
}
