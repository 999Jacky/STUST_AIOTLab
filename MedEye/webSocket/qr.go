package main

import (
	"strings"
)

func getCode(str string) string {
	if strings.Contains(str, ".kmuh.") {
		return kmuhURL(str)
	}
	return str
}

func kmuhURL(str string) string {
	// http://www2.kmuh.org.tw/web/DrugSearch/PB.aspx?Search=1AMARM
	return strings.Split(str, "=")[1]
}
