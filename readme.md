# Wetterstation
## Stack
- Flask
- SQLite
## Endpoints
### Submit measurement (POST)
```
http://host/api/submit
```
```json
{
	"device_id": str DEVICE_ID,
	"temperature": int TEMPERATURE,
	"humidity": int HUMIDITY
}
```
**Response**
```json
{
    "status": "STATUS",
}
```
### Get new device ID (GET)
```
http://host/api/new_device_id
```
**Response**
```json
{
	"device_id": str DEVICE_ID
}
```
