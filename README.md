# farm-sense
## <h1> Description</h1>
<p>The aim of the project is to build a mobile/web dashboard with integrated SMS notifications designed for subsistence farmers. It leverages predictive weather patterns from the Weather API to provide timely farming advice such as crop planting suggestions, irrigation reminders, pest/disease alerts, and harvesting schedules</p>.

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
| ----- |-------------------------------|--------------------------------------------------------- |
| 1.    |     WeatherAI                 | Fetch weather forecast based on GET request              |
| 2.    |     AI Agent                  | Recieves data from Weather AI,generates Farming Advice   |
| 3.    |     Callback/Webhook Layer    | Sends AI output to SMS Gateway                           |
| 4.    |     SMS Gateway               | Delivers message to farmer's device                      |
| 5.    |     Dashboard                 | Displaye forecast, AI advice and SMS logs                |

## <h1> Author </h1>

Built by <b>Andrew Indeche</b>