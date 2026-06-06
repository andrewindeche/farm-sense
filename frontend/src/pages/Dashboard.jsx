import { useState, useCallback } from "react";
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
  TextField,
  Button,
  Paper,
  Fade,
} from "@mui/material";
import {
  WbSunny,
  Agriculture,
  BugReport,
  CalendarMonth,
  MyLocation,
} from "@mui/icons-material";

const services = [
  {
    key: "weather",
    title: "Weather",
    icon: <WbSunny sx={{ fontSize: 40 }} />,
    description: "Current conditions and forecast",
    color: "#FB8C00",
    bg: "#FFF3E0",
  },
  {
    key: "crop",
    title: "Crop Advice",
    icon: <Agriculture sx={{ fontSize: 40 }} />,
    description: "Personalized crop recommendations",
    color: "#2E7D32",
    bg: "#E8F5E9",
  },
  {
    key: "pest",
    title: "Pest Alerts",
    icon: <BugReport sx={{ fontSize: 40 }} />,
    description: "Pest and disease warnings",
    color: "#C62828",
    bg: "#FFEBEE",
  },
  {
    key: "harvest",
    title: "Harvest",
    icon: <CalendarMonth sx={{ fontSize: 40 }} />,
    description: "Harvest timing reminders",
    color: "#5D4037",
    bg: "#EFEBE9",
  },
];

const DEFAULT_LAT = -1.2921;
const DEFAULT_LON = 36.8219;

export default function Dashboard() {
  const navigate = useNavigate();
  const [lat, setLat] = useState(DEFAULT_LAT);
  const [lon, setLon] = useState(DEFAULT_LON);
  const [activeKey, setActiveKey] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const token = localStorage.getItem("token");
  if (!token) {
    navigate("/login");
    return null;
  }

  const fetchAdvice = useCallback(
    async (key) => {
      setActiveKey(key);
      setLoading(true);
      setError("");
      setResult(null);

      try {
        let data;

        if (key === "weather") {
          const res = await fetch(
            `/api/weather/current?lat=${lat}&lon=${lon}`,
          );
          data = await res.json();
          if (!res.ok) throw new Error(data.detail || "Failed to fetch weather");
          data = data.current || data;
        } else {
          const endpoint =
            key === "crop"
              ? "/api/advice/request"
              : key === "pest"
                ? "/api/advice/pest-disease"
                : "/api/advice/harvest-reminder";

          const res = await fetch(endpoint, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ lat, lon }),
          });
          data = await res.json();
          if (!res.ok) throw new Error(data.detail || "Request failed");
        }

        setResult(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    },
    [lat, lon],
  );

  const renderResult = () => {
    if (loading) {
      return (
        <Box sx={{ textAlign: "center", py: 6 }}>
          <CircularProgress />
          <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
            Fetching {services.find((s) => s.key === activeKey)?.title.toLowerCase()} advice...
          </Typography>
        </Box>
      );
    }

    if (error) {
      return (
        <Alert severity="error" sx={{ my: 2 }}>
          {error}
        </Alert>
      );
    }

    if (!result) return null;

    if (activeKey === "weather") {
      return (
        <Box
          sx={{ display: "flex", alignItems: "center", gap: 3, flexWrap: "wrap" }}
        >
          <WbSunny sx={{ fontSize: 64, color: "#FB8C00" }} />
          <Box>
            <Typography variant="h2" sx={{ fontWeight: 900, lineHeight: 1 }}>
              {result.temp_c ?? result.temperature ?? "--"}&deg;C
            </Typography>
            <Typography variant="body1" color="text.secondary">
              {result.condition?.text ?? "Clear"} &middot; Humidity:{" "}
              {result.humidity ?? "--"}%
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Wind: {result.wind_kph ?? "--"} km/h &middot; Precipitation:{" "}
              {result.precip_mm ?? "--"} mm
            </Typography>
          </Box>
        </Box>
      );
    }

    const text =
      result.recommendation || result.alert || result.reminder || "";
    const sent = result.sent;

    return (
      <Box>
        <Typography variant="body1" sx={{ whiteSpace: "pre-line", mb: 1 }}>
          {text}
        </Typography>
        {sent !== undefined && (
          <Typography
            variant="caption"
            color={sent ? "success.main" : "warning.main"}
          >
            {sent ? "SMS sent successfully" : "SMS delivery failed"}
          </Typography>
        )}
      </Box>
    );
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" color="primary.dark" gutterBottom>
        Welcome, {localStorage.getItem("username") || "Farmer"}
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
        Enter your farm coordinates and click a card to get started
      </Typography>

      <Paper elevation={0} sx={{ p: 3, mb: 4, border: "1px solid", borderColor: "divider" }}>
        <Box
          sx={{
            display: "flex",
            alignItems: "flex-end",
            gap: 2,
            flexWrap: "wrap",
          }}
        >
          <MyLocation sx={{ color: "primary.main", mb: 0.5 }} />
          <TextField
            label="Latitude"
            type="number"
            size="small"
            value={lat}
            onChange={(e) => setLat(parseFloat(e.target.value) || 0)}
            sx={{ maxWidth: 160 }}
            inputProps={{ step: 0.0001 }}
          />
          <TextField
            label="Longitude"
            type="number"
            size="small"
            value={lon}
            onChange={(e) => setLon(parseFloat(e.target.value) || 0)}
            sx={{ maxWidth: 160 }}
            inputProps={{ step: 0.0001 }}
          />
          <Typography variant="caption" color="text.secondary" sx={{ alignSelf: "center" }}>
            Defaults: Nairobi (-1.2921, 36.8219)
          </Typography>
        </Box>
      </Paper>

      <Grid container spacing={3} sx={{ mb: 4 }}>
        {services.map((item) => {
          const isActive = activeKey === item.key;
          return (
            <Grid size={{ xs: 12, sm: 6, md: 3 }} key={item.key}>
              <Card
                onClick={() => fetchAdvice(item.key)}
                sx={{
                  cursor: "pointer",
                  transition: "0.25s",
                  border: isActive ? 2 : 1,
                  borderColor: isActive ? item.color : "divider",
                  bgcolor: isActive ? item.bg : "background.paper",
                  "&:hover": {
                    transform: "translateY(-4px)",
                    boxShadow: "0 8px 24px rgba(0,0,0,0.12)",
                    borderColor: item.color,
                  },
                }}
              >
                <CardContent sx={{ textAlign: "center", py: 4 }}>
                  <Box sx={{ color: item.color, mb: 1 }}>{item.icon}</Box>
                  <Typography variant="h6" color="primary.dark">
                    {item.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {item.description}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          );
        })}
      </Grid>

      {(result || loading || error) && (
        <Fade in timeout={300}>
          <Paper elevation={1} sx={{ p: 4, borderRadius: 3 }}>
            <Typography variant="h6" color="primary.dark" gutterBottom>
              {services.find((s) => s.key === activeKey)?.title}
            </Typography>
            {renderResult()}
          </Paper>
        </Fade>
      )}
    </Container>
  );
}
