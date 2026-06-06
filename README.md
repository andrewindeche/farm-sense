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

2. Set Up Python Backend (FastAPI)
```bash
python3 -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Environment variables
```bash
WEATHER_API_KEY=your_weatherai_key
AFRICASTALKING_USERNAME=sandbox
AFRICASTALKING_API_KEY=your_africastalking_api_key
AFRICASTALKING_SENDER_ID=FARMSENSE
FARMER_PHONE=+2547XXXXXXXX
```

5. Run the backend
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

6. Backend API routes
- `GET /api/weather/current?lat=<lat>&lon=<lon>`
- `GET /api/weather/forecast?lat=<lat>&lon=<lon>&days=<days>`
- `POST /api/notify/farmer?message=<text>`

7. Postman usage
- Do not send secret keys from Postman.
- Your `.env` file on the server provides the WeatherAI and Africa's Talking credentials.
- In Postman, only send query parameters for the endpoints above.

8. Set Up Frontend Dashboard
React
```bash
npx create-react-app dashboard
cd dashboard
npm install axios
npm start
```

7. Schedule Locally (cron job)
```bash 
crontab -e
```

Example entry (send advice every morning at 7 AM):
```bash
0 7 * * * /path/to/venv/bin/python /path/to/farm-sense/send_sms.py
```

## <h1> Author </h1>

Built by <b>Andrew Indeche</b>