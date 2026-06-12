import { useMemo } from "react";
import { Grid, Card, CardContent, Typography, Box } from "@mui/material";
import {
  WbSunny,
  Agriculture,
  BugReport,
  CalendarMonth,
} from "@mui/icons-material";
import { useSelector, useDispatch } from "react-redux";
import { fetchStart, fetchSuccess, fetchFail } from "../store/slices/adviceSlice";
import { apiFetch } from "../lib/api";

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

export default function AdviceCards() {
  const dispatch = useDispatch();
  const { lat, lon } = useSelector((s) => s.location);
  const activeKey = useSelector((s) => s.advice.activeKey);

  const fetchAdvice = async (key) => {
    dispatch(fetchStart(key));
    try {
      let data;
      if (key === "weather") {
        const res = await apiFetch(`/api/weather/current?lat=${lat}&lon=${lon}`);
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
        const res = await apiFetch(endpoint, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ lat, lon }),
        });
        data = await res.json();
        if (!res.ok) throw new Error(data.detail || "Request failed");
      }
      dispatch(fetchSuccess(data));
    } catch (err) {
      dispatch(fetchFail(err.message));
    }
  };

  const cards = useMemo(
    () =>
      services.map((item) => {
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
      }),
    [activeKey, lat, lon],
  );

  return (
    <Grid container spacing={3} sx={{ mb: 4 }}>
      {cards}
    </Grid>
  );
}
