package main

import (
	"database/sql"
	"errors"
	_ "github.com/go-sql-driver/mysql"
	"strings"
	"time"
)

var DB *sql.DB
var UsingFakeDB bool = false

func ConnectDB() {
	if UsingFakeDB {
		Log.Warnln("Using FakeDB")
		return
	}
	var err error
	DB, err = sql.Open("mysql", "user:abc123@/Med?parseTime=true")
	if err != nil {
		Log.Errorln(err)
	}
	err = DB.Ping()
	if err != nil {
		Log.Errorln(err)
		time.Sleep(1 * time.Second)
		Log.Infoln("Reconnecting DB")
		ConnectDB()
	}
	TestDB4MedEye()
	Log.Debugln("Success Connect to DB")
}

func AddMedEyeAccount() error {
	if UsingFakeDB {
		return nil
	}
	stmt, err := DB.Prepare("insert Stafes(id,job_code, name, passwd)  values (?,?,?,?)")
	if err != nil {
		return err
	}
	_, err = stmt.Exec(0, "D", "MedEye", Md5("MedEye"))
	if err != nil {
		return err
	}
	_, err = DB.Exec("update Stafes set id=0 where name=?", "MedEye")
	if err != nil {
		return err
	}
	return nil
}

func AddDocAccount(docName string, jobCode string, passWd string) error {
	if UsingFakeDB {
		return nil
	}
	isNotExist, err := CheckDocIsNOTExist(docName)
	if err != nil {
		return err
	}
	if !isNotExist {
		return errors.New("帳號已存在")
	}
	stmt, err := DB.Prepare("insert Stafes(job_code, name, passwd)  values (?,?,?)")
	if err != nil {
		return err
	}
	_, err = stmt.Exec(jobCode, docName, passWd)
	if err != nil {
		return err
	}
	return nil
}

func AddPatients(personalID string, name string) error {
	if UsingFakeDB {
		return nil
	}
	stmt, err := DB.Prepare("insert Patients(personal_id, name)  values (?,?)")
	if err != nil {
		return err
	}
	_, err = stmt.Exec(personalID, name)
	if err != nil {
		return err
	}
	return nil
}

func AddNewPrescription(patientsID string, stafesID int, PType string) (int64, error) {
	if UsingFakeDB {
		return 1, nil
	}
	stmt, err := DB.Prepare("insert Prescription(patients_id, stafes_id, type, timestamp) VALUES (?,?,?,?)")
	if err != nil {
		return 0, err
	}
	res, err := stmt.Exec(patientsID, stafesID, PType, time.Now())
	if err != nil {
		return 0, err
	}
	pid, _ := res.LastInsertId()
	return pid, nil
}

func AddMkupPrescription(pid int64, medCode string) error {
	if UsingFakeDB {
		return nil
	}
	stmt, err := DB.Prepare("insert MKUPPrescription(pid, med_code) VALUES (?,?)")
	if err != nil {
		return err
	}
	_, err = stmt.Exec(pid, medCode)
	if err != nil {
		Log.Errorln("新增mkup失敗")
		return err
	}
	return nil
}

func CheckDocIsNOTExist(docName string) (bool, error) {
	row, err := DB.Query("select  * from Stafes where name=?", docName)
	if err != nil {
		return false, err
	}
	for row.Next() {
		return false, nil
	}
	return true, nil
}

func GetDocInfo(docName string, passwd string) (DocInfoStruct, error) {
	if UsingFakeDB {
		if docName != "ABC" {
			return DocInfoStruct{}, errors.New("帳號不存在或密碼錯誤")
		}
		return DocInfoStruct{
			StafesID: 1,
			JobCode:  "D",
			Name:     "ABC",
		}, nil
	}
	row := DB.QueryRow("select * from Stafes where name=? and passwd=?", docName, passwd)
	d := DocInfoStruct{}
	var uid int
	var name string
	var jobCode string
	var pwd string
	err := row.Scan(&uid, &jobCode, &name, &pwd)
	if err != nil {
		return d, err
	}
	// TODO: 不需要下面if
	if pwd != passwd || name == "" {
		return d, errors.New("帳號不存在或密碼錯誤")
	}
	d = DocInfoStruct{
		StafesID: uid,
		JobCode:  jobCode,
		Name:     name,
	}

	return d, nil
}

func GetPrescriptionMedsInfo(pid float64) ([]string, error) {
	if UsingFakeDB {
		return []string{"AAA", "BBB"}, nil
	}
	rows, err := DB.Query("SELECT med_code from MKUPPrescription where PID=?", pid)
	if err != nil {
		return nil, err
	}
	meds := make([]string, 0)
	for rows.Next() {
		medCode := ""
		rows.Scan(&medCode)
		meds = append(meds, medCode)
	}
	return meds, nil
}

func GetPatientsInfoFromPID(pid float64) PrescriptionInfoStruct {
	if UsingFakeDB {
		return PrescriptionInfoStruct{
			PersonalID: "A123456789",
			StafesID:   1,
			Type:       "病房",
			MedList:    []string{"AAA", "BBB"},
		}
	}
	row := DB.QueryRow("SELECT * from Prescription where PID=?", pid)
	p := 0
	personalID := ""
	stafesID := 0
	pType := ""
	timestamp := time.Time{}
	row.Scan(&p, &personalID, &stafesID, &pType, &timestamp)

	return PrescriptionInfoStruct{
		PersonalID: personalID,
		StafesID:   stafesID,
		Type:       pType,
		MedList:    nil,
	}
}

func GetPrescriptionInfosFromTime(timeStart string, timeEnd string) ([]float64, []float64, []string, error) {
	if UsingFakeDB {
		return []float64{1, 2}, []float64{1, 2}, []string{"MedPlus", "MedPlus"}, nil
	}
	var rows *sql.Rows
	var err error
	pids := make([]float64, 0)
	dids := make([]float64, 0)
	machineTypes := make([]string, 0)
	if timeStart != "" {
		query := "Select PID,DID,stafes_id from Detection where timestamp between ? and ?"
		rows, err = DB.Query(query, timeStart, timeEnd)
	} else {
		query := "Select PID,DID,stafes_id from Detection"
		rows, err = DB.Query(query)
	}
	if err != nil {
		return nil, nil, nil, err
	}
	for rows.Next() {
		pid := float64(0)
		did := float64(0)
		id := float64(-1)
		rows.Scan(&pid, &did, &id)
		pids = append(pids, pid)
		dids = append(dids, did)
		if id == 0 {
			machineTypes = append(machineTypes, "MedEye")
		} else {
			machineTypes = append(machineTypes, "MedPlus")
		}
	}
	return pids, dids, machineTypes, nil
}

func GetPatientName(perionalID string) string {
	if UsingFakeDB {
		return "abc"
	}
	row := DB.QueryRow("select name from Patients where personal_id=?", perionalID)
	name := ""
	row.Scan(&name)
	return name
}

func SetDetectionInfo(pid float64, stafesID int, machineMac string) (float64, error) {
	if UsingFakeDB {
		return 1, nil
	}
	stmt, err := DB.Prepare("insert Detection(pid, stafes_id, machine, timestamp) values (?,?,?,?)")
	if err != nil {
		return 0, err
	}
	res, err := stmt.Exec(pid, stafesID, machineMac, time.Now())
	if err != nil {
		return 0, err
	}
	did, _ := res.LastInsertId()
	return float64(did), nil
}

func GetResultFromDidAndMedCode(dids []float64, medCodes []string) {

}

func GetResultFromDid(dids []float64) ([]ResultListStruct, error) {
	if UsingFakeDB {
		r := make([]ResultListStruct, 0)
		for _, v := range dids {
			if v == 1 {
				r = append(r, ResultListStruct{
					DID:     1,
					MedCode: "AAA",
				})
				r = append(r, ResultListStruct{
					DID:     1,
					MedCode: "BBB",
				})
			}
			if v == 2 {
				r = append(r, ResultListStruct{
					DID:     2,
					MedCode: "BBB",
				})
			}
		}
		return r, nil
	}
	if len(dids) == 0 {
		return nil, nil
	}
	args := make([]interface{}, len(dids))
	for i, v := range dids {
		args[i] = v
	}
	rows, err := DB.Query("select DID,med_code from result where DID in (?"+strings.Repeat(",?", len(args)-1)+`)`, args...)
	if err != nil {
		return nil, err
	}
	rls := make([]ResultListStruct, 0)
	for rows.Next() {
		t := ResultListStruct{}
		rows.Scan(&t.DID, &t.MedCode)
		rls = append(rls, t)
	}
	return rls, nil
}

func GetMkupPrescritptionFromPid(pids []float64) ([]MkupPrescriptionListStruct, error) {
	if UsingFakeDB {
		r := make([]MkupPrescriptionListStruct, 0)
		for _, v := range pids {
			r = append(r, MkupPrescriptionListStruct{
				PID:     v,
				MedCode: "AAA",
			})
			r = append(r, MkupPrescriptionListStruct{
				PID:     v,
				MedCode: "BBB",
			})
		}
		return r, nil
	}
	if len(pids) == 0 {
		return nil, nil
	}
	args := make([]interface{}, 0)
	tmap := make(map[float64]bool)
	for _, v := range pids {
		if _, ok := tmap[v]; !ok {
			tmap[v] = true
			args = append(args, v)
		}
	}
	rows, err := DB.Query("select PID,med_code from MKUPPrescription where PID in (?"+strings.Repeat(",?", len(args)-1)+`)`, args...)
	if err != nil {
		return nil, err
	}
	mkpl := make([]MkupPrescriptionListStruct, 0)
	for rows.Next() {
		t := MkupPrescriptionListStruct{}
		rows.Scan(&t.PID, &t.MedCode)
		mkpl = append(mkpl, t)
	}
	return mkpl, nil
}

func GetMachineMacFormDID(did string) string {
	if UsingFakeDB {
		return "MAC"
	}
	row := DB.QueryRow("select machine from Detection where DID =?", did)
	mac := ""
	row.Scan(&mac)
	return mac
}

func SetResult(Did float64, medCode string) error {
	if UsingFakeDB {
		return nil
	}
	stmt, err := DB.Prepare("INSERT result(did, med_code)  values (?,?)")
	if err != nil {
		return err
	}
	_, err = stmt.Exec(Did, medCode)
	if err != nil {
		return err
	}
	return nil
}

/*
SQL
select CURRENT_TIMESTAMP() 獲得目前timestamp

MedList(預先建好) ->prescription(藥單資料) -> mkuppre...
*/
