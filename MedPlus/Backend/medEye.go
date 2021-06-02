package main

type MedEyeMsgStruct struct {
	Status int    `json:"status"`
	Qr     string `json:"qr"`
	Cam    []struct {
		MedID string `json:"med_id"`
		Count int    `json:"count"`
	} `json:"cam"`
	ImgURL   string        `json:"img_url"`
	UnFilter []interface{} `json:"un_filter"`
}

func RecvMedEyeData(data map[string]interface{}) {
	qrcode := data["qr"].(string)
	cam := make([]string, 0)
	for _, v := range data["cam"].([]interface{}) {
		m := v.(map[string]interface{})["med_id"]
		cam = append(cam, m.(string))
	}
	pid, err := AddNewPrescription("E111111111", 0, "門診")
	if err != nil {
		Log.Errorln(err)
		return
	}
	err = AddMkupPrescription(pid, qrcode)
	if err != nil {
		Log.Errorln(err)
		return
	}
	did, err := SetDetectionInfo(float64(pid), 0, "MedEye")
	if err != nil {
		Log.Errorln(err)
		return
	}
	for _, v := range cam {
		err := SetResult(did, v)
		if err != nil {
			Log.Errorln(err)
		}
	}
}

func TestDB4MedEye() {
	Log.Debugln("Testing DB For MedEye")
	b, err := CheckDocIsNOTExist("MedEye")
	if err != nil {
		Log.Errorln(err)
		return
	}
	if b {
		Log.Debugln("Adding MedEye account")
		err := AddMedEyeAccount()
		if err != nil {
			Log.Errorln(err)
		}
		err = AddPatients("E111111111", "MedEye")
		if err != nil {
			Log.Errorln(err)
		}
	}
}
