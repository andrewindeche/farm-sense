# farm-sense

| Tool                      | Description                     | Tags for tools used             |
| ------------------------- | ------------------------------- | ------------------------------- |
| 1.GitHub                  | Version Control                 | [Version-Control]; [Repository];|
| 2.Weather API             | REST API                        | [REST]; [Request];              |
| 3.GitHub                  | Version Control                 | [Version-Control]; [Repository];|
| 4.Africa's Talking        | SMS Gateway                     | [SMS]; [Low-Latency];           |
| 5.Firebase cloud Messaging| Push Notification               | [Push-Notification];            |
| 6.ReactJs                 | Frontend Library                | [Frontend]; [Javascript];       |
| 7.FastApi                 | Backend Framework               | [Backend]; [Python];            |
| 8.CronJob                 | Schedule jobs                   | [Jobs]; [Scheduler];            |

## <h1> Description</h1>

<p>The aim of the project is to build a mobile/web dashboard with integrated SMS notifications designed for subsistence farmers. It leverages predictive weather patterns from the Weather API to provide timely farming advice such as crop planting suggestions, irrigation reminders, pest/disease alerts, and harvesting schedules</p>

## <h1> Features</h1>

<ul>
<li>Weather-driven task notifications (periodic SMS/app alerts).</li>
<li>Beginner-friendly crop recommendations based on seasonal forecasts.</li>
<li>Low-latency rural design with SMS fallback for areas with poor internet.</li>
<li>Crop Suggestionsto Map weather and season and recommend crops.</li>
<li>Pest/Disease Alerts based on humidity and temperature rules.</li>
<li>Harvest Reminders Based on crop cycle length e.g. maize ~90 days.</li>
</ul>

## <h1> Architeture and Flow</h1>

| Step  | Feature                       | Role                                                     |
| ----- | ----------------------------- | -------------------------------------------------------- |
| 1.    |     WeatherAI                 | Fetch weather forecast based on GET request or Cronjob   |
| 2.    |     AI Agent/FastAPI          | Recieves data from Weather AI,generates Farming Advice   |
| 3.    |     Callback/Webhook Layer    | Sends AI output to SMS Gateway                           |
| 4.    |     SMS Gateway               | Delivers message to farmer's device                      |
| 5.    |     Dashboard                 | Displaye forecast, AI advice and SMS logs                |

## <h1> Set up Instructions</h1>

1. Clone the Repository

```bash
git clone https://github.com/andrewindeche/farm-sense.git
cd farm-sense
```

2. Set Up Backend (FastAPI + WeatherAI)

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate   # Linux/Mac
.venv\Scripts\activate      # Windows
pip install -r requirements.txt
```

3. Environment variables

Create `backend/.env`:
```bash
WEATHER_API_KEY=your_weatherai_key
AFRICASTALKING_USERNAME=sandbox
AFRICASTALKING_API_KEY=your_africastalking_api_key
AFRICASTALKING_SENDER_ID=FARMSENSE
FARMER_PHONE=+2547XXXXXXXX
```

4. Run the backend

```bash
uvicorn app.main:app --reload --port 8001
```

5. Backend API Routes

**Health**
- `GET /` — root check
- `GET /health` — health status

**Authentication**
- `POST /api/auth/register` — body: `{"username":"user","password":"pass"}`
- `POST /api/auth/login` — body: `{"username":"user","password":"pass"}`
- `GET /api/auth/me` — header: `Authorization: Bearer <token>`
- `POST /api/auth/logout` — header: `Authorization: Bearer <token>`

**Weather (WeatherAI)**
- `GET /api/weather/current?lat=-1.2921&lon=36.8219` — current conditions by coordinates
- `GET /api/weather/forecast?lat=-1.2921&lon=36.8219&days=7` — forecast (1-7 days)

**SMS Notifications (Africa's Talking)**
- `POST /api/notify/farmer?message=Water+your+crops` — send SMS to farmer

6. Run tests

```bash
.venv/bin/python -m pytest -q
```

7. Postman Usage

- API keys are loaded from `backend/.env` on the server
- Do not send credentials in Postman headers
- Send only query parameters and JSON payloads to public routes

8. Set Up Frontend Dashboard
React
```bash
npx create-react-app dashboard
cd dashboard
npm install axios
npm start
```

9. Schedule Locally (cron job)
```bash 
crontab -e
```

Example entry (send advice every morning at 7 AM):
```bash
0 7 * * * /path/to/venv/bin/python /path/to/farm-sense/send_sms.py
```

## <h1> Author </h1>

Built by <b>Andrew Indeche</b>