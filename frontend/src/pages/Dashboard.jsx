import { Container, Typography, Paper, Box, TextField } from "@mui/material";
import { MyLocation } from "@mui/icons-material";
import { useDispatch, useSelector } from "react-redux";
import { setLocation } from "../store/slices/locationSlice";
import AdviceCards from "../components/AdviceCards";
import AdviceResult from "../components/AdviceResult";
import SchedulerPanel from "../components/SchedulerPanel";

export default function Dashboard() {
  const dispatch = useDispatch();
  const { lat, lon } = useSelector((s) => s.location);

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" color="primary.dark" gutterBottom>
        Welcome, {localStorage.getItem("username") || "Farmer"}
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
        Enter your farm coordinates and click a card to get started
      </Typography>

      <Paper elevation={0} sx={{ p: 3, mb: 4, border: "1px solid", borderColor: "divider" }}>
        <Box sx={{ display: "flex", alignItems: "flex-end", gap: 2, flexWrap: "wrap" }}>
          <MyLocation sx={{ color: "primary.main", mb: 0.5 }} />
          <TextField
            label="Latitude"
            type="number"
            size="small"
            value={lat}
            onChange={(e) => dispatch(setLocation({ lat: parseFloat(e.target.value) || 0, lon }))}
            sx={{ maxWidth: 160 }}
            inputProps={{ step: 0.0001 }}
          />
          <TextField
            label="Longitude"
            type="number"
            size="small"
            value={lon}
            onChange={(e) => dispatch(setLocation({ lat, lon: parseFloat(e.target.value) || 0 }))}
            sx={{ maxWidth: 160 }}
            inputProps={{ step: 0.0001 }}
          />
          <Typography variant="caption" color="text.secondary" sx={{ alignSelf: "center" }}>
            Defaults: Nairobi (-1.2921, 36.8219)
          </Typography>
        </Box>
      </Paper>

      <AdviceCards />
      <AdviceResult />
      <SchedulerPanel />
    </Container>
  );
}
