**<h1> URLS </h1>**
- **<h2> /api/v1/authorization </h2>**
 **<h3> POST </h3>**
 **<h4> Expect json data: </h4>**
```json
{
  "phone_number": "PHONE NUMBER"
} 
```
**<h4> Now it returns verify code, but in production, must return None and send code in sms</h4>**
- **<h2> /api/v1/verify </h2>**
 **<h4> Expect json data: </h4>**
```json
{
  "verify_code": "VERIFY CODE"
} 
```
**<h4> If valid => set in your cookie sessionid, now you can get or post /api/v1/me </h4>**
- **<h2> /api/v1/me </h2>**
 **<h3> GET </h3>**
 **<h4> No need data </h4>**
 **<h4> Response example: </h4>**
```json
{
    "phone_number": "PHONE NUMBER",
    "invite_code": "invite_code",
    "invitation_code": "invitation_code",
    "invited_users": [
        {"phone_number": "PHONE_NUMBER"}
    ]
}
```
 **<h3> POST </h3>**
 **<h4> Expect json data: </h4>**
```json
{
  "invite_code": "INVITE CODE"
} 
```
