## ✅ Start in `Docker`

```bash
docker-compose up --build 
```
Visit `http://localhost:5085` in your browser. The app should be up & running.


## ✅ Manual Build
Install modules via VENV (windows)
-------------------------------------------------------------
virtualenv env

.\env\Scripts\activate

pip install -r requirements.txt


Set Up Flask Environment
-------------------------------------------------------------

$env:FLASK_APP = ".\run.py"

$env:FLASK_ENV = "development"


Start the app
------------------------------------------------------------
flask run

flask run --cert=adhoc # For HTTPS server

```powershell
set FLASK_APP=".\run.py"
set FLASK_ENV="development"
set FLASK_DEBUG=1
flask run
```

```powershell
export FLASK_APP=".\run.py"
export FLASK_ENV="development"
export FLASK_DEBUG=1
flask run
```

