using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using System.Windows.Forms;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using WebSocketSharp;

namespace DecationTest {
    public partial class Form1 : Form {
        public class sendConn {
            public int status;
        }

        public class recvMsg {
            public int status;
            public string qr;
            public string img_url;
            public camStruct[] cam;
            public camStruct[] un_filter;
        }

        public class camStruct {
            public string med_id;
            public int count;
        }

        public Form1() {
            InitializeComponent();
        }

        WebSocket ws = new WebSocket("ws://192.168.10.1:3000/ws");
        private int errConn = 0;

        private void Form1_Load(object sender, EventArgs e) {
            ws.OnOpen += Ws_OnOpen;
            ws.OnMessage += Ws_OnMessage;
            ws.OnError += Ws_OnError;
            ws.OnClose += Ws_OnClose;
            ws.ConnectAsync();
        }

        private void Ws_OnClose(object sender, CloseEventArgs e) {
            errConn++;
            this.Invoke(new Action((() => { label1.Text = "連線失敗." + errConn; })));
            Thread.Sleep(1000);
            ws.Connect();
        }

        private void Ws_OnError(object sender, ErrorEventArgs e) {
            this.Invoke(new Action((() => { label1.Text = "連線失敗." + errConn; })));
            Thread.Sleep(1000);
            ws.Connect();
        }

        private void Ws_OnMessage(object sender, MessageEventArgs e) {
            recvMsg r = JsonConvert.DeserializeObject<recvMsg>(e.Data);
            if (r.status == 4) {
                this.Invoke(new Action((() => label1.Text = "已連線")));
                return;
            }

            updateUi(r);
            sendConn o = new sendConn();
            o.status = 2;
            string json = JsonConvert.SerializeObject(o);
            ws.Send(json);
        }

        private void updateUi(recvMsg msg) {
            var text = "";
            var textOrg = "";
            var ok = false;
            foreach (var result in msg.cam) {
                text += result.med_id + "：" + result.count + ",";
                if (result.med_id == msg.qr) {
                    ok = true;
                } else {
                    ok = false;
                }
            }
            foreach (var result in msg.un_filter) {
                textOrg += result.med_id + "：" + result.count + ",";
            }

            var d = msg.img_url.Replace("_org", "");
            Thread.Sleep(200);
            this.Invoke(new Action((() => {
                label1.Text = "";
                try {
                    pictureBox1.Load(msg.img_url);
                    pictureBox2.Load(d);
                } catch (Exception e) {
                    label1.Text = e.ToString() + "   ";
                }

                label2.Text = msg.qr;
                label1.Text += text;
                if (ok) {
                    label1.ForeColor = Color.Green;
                } else {
                    label1.ForeColor = Color.Red;
                }

                label1.Text += "\n" + textOrg;
            })));
        }

        private void Ws_OnOpen(object sender, EventArgs e) {
            sendConn o = new sendConn();
            o.status = 1;
            string json = JsonConvert.SerializeObject(o);
            ws.Send(json);
        }
    }
}
