import gspread
import numpy as np
import cv2 as cv
gc = gspread.oauth()

sh = gc.open("Screen")
cam = cv.VideoCapture(1)

ret, frame = cam.read()
if not ret:
	raise RuntimeError("Failed to capture image from camera")

img = cv.imread("image.png")
if img is None:
	raise FileNotFoundError("image.png could not be loaded")

imagesize = (100, 100)
resized_img = cv.cvtColor(cv.resize(img, imagesize), cv.COLOR_BGR2RGB)

worksheet = sh.get_worksheet_by_id(0)
worksheet.resize(rows=imagesize[0], cols=imagesize[1])

cell_size = 20
format_requests = [
	{
		"updateDimensionProperties": {
			"range": {
				"sheetId": worksheet.id,
				"dimension": "ROWS",
				"startIndex": 0,
				"endIndex": imagesize[1],
			},
			"properties": {"pixelSize": cell_size},
			"fields": "pixelSize",
		}
	},
	{
		"updateDimensionProperties": {
			"range": {
				"sheetId": worksheet.id,
				"dimension": "COLUMNS",
				"startIndex": 0,
				"endIndex": imagesize[0],
			},
			"properties": {"pixelSize": cell_size},
			"fields": "pixelSize",
		}
	},
]
sh.batch_update({"requests": format_requests})

while True:
    ret, img = cam.read()  
    if not ret:
        break
    img = cv.resize(img, imagesize)
    img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
    img = cv.blur(img, (3, 1))  
    rows = [
        {
            "values": [
                {
                    "userEnteredFormat": {
                        "backgroundColor": {
                            "red": int(red) / 255,
                            "green": int(green) / 255,
                            "blue": int(blue) / 255,
                        }
                    }
                }
                for red, green, blue in row
            ]
        }
        for row in img
    ]
    cv.imshow("Camera Feed", img)
    if cv.waitKey(1) & 0xFF == ord("q"):
        break
    sh.batch_update({
        "requests": [{
            "updateCells": {
                "rows": rows,
                "start": {
                    "sheetId": worksheet.id,
                    "rowIndex": 0,
                    "columnIndex": 0,
                },
                "fields": "userEnteredFormat.backgroundColor",
            }
        }]
    })



