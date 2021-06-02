### status狀態
+ 1 : App加入ws連線
+ 2 : 等待回傳
+ 3 : 辨識結果
+ 4 : OK


### App連線

+ 建立連線：傳status:1，server會回傳status:4

#### ws://192.168.10.1:3000/ws

``` json
{
    "status":1
}
```

+ 等待辨識結果：傳status:2

辨識結果回傳
``` json
{
  "status": 3,
  "qr": "abc123",
  "cam": [
    {
      "med_id": "abc",
      "count": 10
    },
    {
      "med_id": "abc",
      "count": 10
    }
  ]
}
```

+ 開機狀態
```text
http://192.168.10.1:3000/stat
```
回傳"true"或"false"
