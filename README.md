# farm-sense

| Tool                      | Description                     | Tags for tools used             |
| ------------------------- | ------------------------------- | ------------------------------- |
| 1.GitHub                  | Version Control                 | [Version-Control]; [Repository];|
| 2.WeatherAI API             | REST API                        | [REST]; [Request];              |
| 3.GitHub                  | Version Control                 | [Version-Control]; [Repository];|
| 4.Africa's Talking        | SMS Gateway                     | [SMS]; [Low-Latency];           |
| 5.Firebase cloud Messaging| Push Notification               | [Push-Notification];            |
| 6.ReactJs                 | Frontend Library                | [Frontend]; [Javascript];       |
| 7.FastApi                 | Backend Framework               | [Backend]; [Python];            |
| 8.CronJob                 | Schedule jobs                   | [Jobs]; [Scheduler];            |

## <h1> Description</h1>

<p>The aim of the project is to build a dashboard with integrated SMS notifications designed for subsistence farmers. It leverages predictive weather patterns from the Weather API to provide timely farming advice such as crop planting suggestions, irrigation reminders, pest/disease alerts, and harvesting schedules</p>

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
python3 -m venv .venv # Linux/Mac
.venv\Scripts\activate      # Windows
pip install -r requirements.txt
```

3. Set Up PostgreSQL Database

Create a new PostgreSQL user and database:

```bash
sudo -u postgres psql
```

Then in the PostgreSQL shell:

```sql
-- Create new user with password
CREATE USER farmsense_user WITH PASSWORD 'your_secure_password_here';

-- Create database
CREATE DATABASE farmsense OWNER farmsense_user;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE farmsense TO farmsense_user;

-- Exit
\q
```

Verify the connection:

```bash
psql -U farmsense_user -d farmsense -h localhost
```

4. Environment variables

Create `backend/.env`:
```bash
DATABASE_URL=postgresql+asyncpg://farmsense_user:your_secure_password_here@localhost:5432/farmsense
WEATHER_API_KEY=your_weatherai_key
AFRICASTALKING_USERNAME=sandbox
AFRICASTALKING_API_KEY=your_africastalking_api_key
AFRICASTALKING_SENDER_ID=AFRICASTKNG
FARMER_PHONE=+2547XXXXXXXX
```

Notes:
- Replace `your_secure_password_here` with the password you set for `farmsense_user`.
- `WEATHER_API_KEY` must be a WeatherAI key, not an Africa's Talking key.
- Africa's Talking keys usually start with `atsk_`; WeatherAI keys use a different prefix.
- Use `AFRICASTALKING_SENDER_ID=AFRICASTKNG` (the default sandbox sender ID) when testing with the Africa's Talking sandbox account.
- For a live Africa's Talking account, set `AFRICASTALKING_SENDER_ID` to your approved sender ID.

5. Run the backend

```bash
uvicorn app.main:app --reload --port 8001
```

6. Backend API Routes

**Rate Limiting**
All endpoints are rate-limited per IP address to prevent abuse (configurable via `slowapi`):
- `GET /`, `GET /health` — 100 requests/minute
- `POST /api/auth/register` — 10 requests/minute
- `POST /api/auth/login` — 20 requests/minute
- `GET /api/auth/me`, `POST /api/auth/logout` — 30 requests/minute
- `GET /api/weather/current`, `GET /api/weather/forecast` — 30 requests/minute (protects WeatherAI API quota)
- `POST /api/advice/request`, `/api/advice/pest-disease`, `/api/advice/harvest-reminder` — 10 requests/minute (each triggers an SMS)
- `POST /api/notify/farmer` — 5 requests/minute (each sends an SMS)
- `GET /api/scheduler/subscribers` — 30 requests/minute
- `POST /api/scheduler/subscribe`, `/api/scheduler/unsubscribe` — 20 requests/minute
- `POST /api/scheduler/deliver-now` — 3 requests/minute (sends SMS to all subscribers)

Exceeding a rate limit returns `429 Too Many Requests`.



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

**Crop Advice**
- `POST /api/advice/request` — request a crop recommendation and send SMS
  - body: `{ "lat": -1.2921, "lon": 36.8219, "farmer_phone": "+254712345678" }`
  - if `farmer_phone` is omitted, the app uses the phone number in `backend/.env`
  - returns a fallback crop recommendation text if AI is unavailable

**SMS Notifications (Africa's Talking)**
- `POST /api/notify/farmer?message=Water+your+crops` — send SMS to farmer

**Pest/Disease Alert**
- `POST /api/advice/pest-disease` — request pest/disease alert and send SMS
  - body: `{ "lat": -1.2921, "lon": 36.8219, "farmer_phone": "+254712345678" }`

**Harvest Reminder**
- `POST /api/advice/harvest-reminder` — request harvest reminder and send SMS
  - body: `{ "lat": -1.2921, "lon": 36.8219, "farmer_phone": "+254712345678" }`

**Cron Job Scheduler**
- `GET /api/scheduler/subscribers` — list all subscribed farmers
- `POST /api/scheduler/subscribe` — subscribe a farmer for daily advice
  - body: `{ "lat": -1.2921, "lon": 36.8219, "phone": "+254712345678" }`
- `POST /api/scheduler/unsubscribe` — unsubscribe a farmer
  - body: `{ "phone": "+254712345678" }`
- `POST /api/scheduler/deliver-now` — trigger immediate advice delivery to all subscribers

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