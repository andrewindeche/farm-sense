import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Box,
  Container,
  Grid,
  Card,
  CardContent,
  Typography,
  CircularProgress,
  Alert,
  Button,
} from "@mui/material";
import {
  WbSunny,
  Agriculture,
  BugReport,
  CalendarMonth,
} from "@mui/icons-material";

const actions = [
  {
    title: "Weather",
    icon: <WbSunny sx={{ fontSize: 40 }} />,
    description: "Current conditions and forecast",
    action: () => {},
  },
  {
    title: "Crop Advice",
    icon: <Agriculture sx={{ fontSize: 40 }} />,
    description: "Personalized crop recommendations",
    action: () => {},
  },
  {
    title: "Pest Alerts",
    icon: <BugReport sx={{ fontSize: 40 }} />,
    description: "Pest and disease warnings",
    action: () => {},
  },
  {
    title: "Harvest",
    icon: <CalendarMonth sx={{ fontSize: 40 }} />,
    description: "Harvest timing reminders",
    action: () => {},
  },
];

export default function Dashboard() {
  const navigate = useNavigate();
  const [weather, setWeather] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      navigate("/login");
      return;
    }

    fetch("/api/weather/current?lat=-1.2921&lon=36.8219", {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((r) => r.json())
      .then((data) => setWeather(data.current || data))
      .catch(() => setError("Could not load weather data"));
  }, [navigate]);

  if (error) {
    return (
      <Container maxWidth="sm" sx={{ mt: 4 }}>
        <Alert severity="warning">{error}</Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" color="primary.dark" gutterBottom>
        Welcome, {localStorage.getItem("username") || "Farmer"}
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        Here is your daily farming overview
      </Typography>

      <Card sx={{ mb: 4, bgcolor: "primary.main", color: "#fff" }}>
        <CardContent>
          <Typography variant="h6" sx={{ color: "#A5D6A7" }}>
            Current Weather
          </Typography>
          {weather ? (
            <Box sx={{ display: "flex", alignItems: "center", gap: 2, mt: 1 }}>
              <WbSunny sx={{ fontSize: 48 }} />
              <Box>
                <Typography variant="h3">
                  {weather.temp_c ?? weather.temperature ?? "--"}&deg;C
                </Typography>
                <Typography variant="body2" sx={{ color: "#C8E6C9" }}>
                  Humidity: {weather.humidity ?? "--"}% &middot;{" "}
                  {weather.condition?.text ?? "Clear"}
                </Typography>
              </Box>
            </Box>
          ) : (
            <CircularProgress color="inherit" size={24} sx={{ mt: 1 }} />
          )}
        </CardContent>
      </Card>

      <Grid container spacing={3}>
        {actions.map((item) => (
          <Grid size={{ xs: 12, sm: 6, md: 3 }} key={item.title}>
            <Card
              sx={{
                cursor: "pointer",
                transition: "0.2s",
                "&:hover": {
                  transform: "translateY(-4px)",
                  boxShadow: "0 8px 24px rgba(0,0,0,0.12)",
                  borderColor: "primary.main",
                },
              }}
              onClick={item.action}
            >
              <CardContent sx={{ textAlign: "center", py: 4 }}>
                <Box sx={{ color: "primary.main", mb: 1 }}>{item.icon}</Box>
                <Typography variant="h6" color="primary.dark">
                  {item.title}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {item.description}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Container>
  );
}
