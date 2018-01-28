Deskripsi endpoint webservice (REST API)
json data container format
{
    'success': boolean,
    'message': 'pesan response',
    'data': data seperti json object, array dsb tergantung dari endpoint yang dipanggil
}



1. Endpoint: www.hostname.com/api/session    POST, DELETE
Data POST response:
{
	"exp": 1519510088,
	"name": "ABDUL ARIS RAHMANUDIN",
	"token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.8LxsYemgyKH18Y-wVLLeOoubT_7p6Sp1b4swD9naNs8",
	"username": "14.14.1.0002"
}
Data DELETE response: None



2. Endpoint: www.hostname.com/api/profile    GET, POST
Data GET response:
{
	"class": {
		"name": "A",
		"prog": "Informatika",
		"type": "Reguler",
		"year": 2017
	},
	"fcm_token": "",
	"name": "Abdul Aris Rahmanudin",
	"type": 1,
	"username": "14.14.1.0002"
}
# jika yang login adalah dosen maka field class tidak ada.

Data POST response: sama dengan response untuk endpoint session/login



3. Endpoint: www.hostname.com/api/token      GET, POST
Data GET response:
{
    "fcm_token": "wVLLeOoubT_7p6Sp1b4swD9naNs8.VoubTwVLLeOoubT"
}
Data POST response: None



4. Endpoint: www.hostname.com/api/announcements      GET
Data GET response:
array of
{
	"attachment": {
    	"mimetype": "image/jpeg",
    	"name": "Wallpaper.jpg",
    	"size": 13471472,
    	"url": "http://localhost:8000/api/announcements/9963b590-614f-464d-a07f-39cd3092516a/attachment/Wallpaper.jpg"
	},
	"description": {
		"content": null,
		"size": 191010,
		"url": "http://localhost:8000/api/announcements/33ff9abe-71f0-401d-aee6-6de6688ad8f8/description"
	},
	"id": "33ff9abe-71f0-401d-aee6-6de6688ad8f8",
	"last_updated": 1512883638.337415,
	"publisher": "Admin",
	"read": true,
	"title": "Lorem ipsum dolor sit amet, consectetur adipisicing elit"
}


5. Endpoint: www.hostname.com/api/announcements/<uuid:obj_id>    GET
Data GET response: sama dengan diatas



6. Endpoint: www.hostname.com/api/announcements/<uuid:pub_id>/description    GET
Data GET response: string deskripsi



7. Endpoint: www.hostname.com/api/announcements/<uuid:pub_id>/attachment/<string:filename>   GET
Data GET response: berkas download (bytes)



8. Endpoint: www.hostname.com/api/announcements/<uuid:pub_id>/read   PUT
Data PUT response: None
