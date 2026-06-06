import { useMemo } from "react";
import { Box, Typography, CircularProgress, Alert, Fade, Paper } from "@mui/material";
import { useSelector, useDispatch } from "react-redux";
import { WbSunny, CheckCircle, Error as ErrorIcon } from "@mui/icons-material";
import { clearAdvice } from "../store/slices/adviceSlice";

const pestKeywords = [
  "aphids", "whiteflies", "armyworms", "spider mites", "thrips",
  "stem borers", "leaf spot", "blight", "powdery mildew", "rust",
  "root rot", "bacterial wilt", "downy mildew", "black sigatoka",
  "leaf rust", "fungal",
];

function AdviceImage({ keywords, activeKey }) {
  const imageKw = useMemo(() => {
    if (activeKey === "pest") {
      const matched = keywords.filter((k) => pestKeywords.includes(k));
      return matched.length ? matched : ["pest", "disease"];
    }
    if (activeKey === "crop") return ["crop", "farming", "agriculture"];
    if (activeKey === "harvest") return ["harvest", "farm"];
    return [];
  }, [keywords, activeKey]);

  if (!imageKw.length) return null;

  return (
    <Box sx={{ display: "flex", gap: 1.5, flexWrap: "wrap", mb: 3 }}>
      {imageKw.slice(0, 4).map((kw) => (
        <Box
          key={kw}
          sx={{
            width: 140,
            height: 100,
            borderRadius: 2,
            overflow: "hidden",
            border: "1px solid",
            borderColor: "divider",
            flexShrink: 0,
          }}
        >
          <img
            src={`https://loremflickr.com/280/200/${encodeURIComponent(kw)}?random=${Date.now()}`}
            alt={kw}
            style={{ width: "100%", height: "100%", objectFit: "cover" }}
            onError={(e) => { e.target.style.display = "none"; }}
          />
        </Box>
      ))}
    </Box>
  );
}

function SmsStatus({ result }) {
  const sent = result.sent;
  if (sent === undefined) return null;

  return (
    <Box
      sx={{
        p: 2,
        borderRadius: 2,
        bgcolor: sent ? "#E8F5E9" : "#FFF8E1",
        border: 1,
        borderColor: sent ? "#A5D6A7" : "#FFE082",
      }}
    >
      <Box sx={{ display: "flex", alignItems: "center", gap: 1, mb: 1 }}>
        {sent ? (
          <CheckCircle fontSize="small" color="success" />
        ) : (
          <ErrorIcon fontSize="small" color="warning" />
        )}
        <Typography variant="subtitle2" color={sent ? "success.dark" : "warning.dark"}>
          {sent ? "SMS delivered successfully" : "SMS delivery failed"}
        </Typography>
      </Box>
      {sent && (
        <Box sx={{ display: "flex", flexWrap: "wrap", gap: 3, ml: 4 }}>
          {result.sms_sender_id && (
            <Box>
              <Typography variant="caption" color="text.secondary">Sender ID</Typography>
              <Typography variant="body2" fontWeight={600}>{result.sms_sender_id}</Typography>
            </Box>
          )}
          {result.sms_response?.SMSMessageData?.Recipients?.[0] && (
            <>
              <Box>
                <Typography variant="caption" color="text.secondary">Recipient</Typography>
                <Typography variant="body2" fontWeight={600}>
                  {result.sms_response.SMSMessageData.Recipients[0].number}
                </Typography>
              </Box>
              <Box>
                <Typography variant="caption" color="text.secondary">Status</Typography>
                <Typography variant="body2" fontWeight={600}>
                  {result.sms_response.SMSMessageData.Recipients[0].status}
                  {result.sms_response.SMSMessageData.Recipients[0].cost &&
                    ` \u00b7 ${result.sms_response.SMSMessageData.Recipients[0].cost}`}
                </Typography>
              </Box>
            </>
          )}
        </Box>
      )}
      {!sent && result.sms_error && (
        <Typography variant="body2" color="warning.dark" sx={{ ml: 4 }}>
          {result.sms_error}
        </Typography>
      )}
    </Box>
  );
}

export default function AdviceResult() {
  const { activeKey, result, loading, error } = useSelector((s) => s.advice);

  if (!activeKey && !result && !loading && !error) return null;

  const title =
    activeKey === "weather"
      ? "Weather"
      : activeKey === "crop"
        ? "Crop Advice"
        : activeKey === "pest"
          ? "Pest Alerts"
          : "Harvest";

  if (loading) {
    return (
      <Fade in timeout={300}>
        <Paper elevation={1} sx={{ p: 4, borderRadius: 3, mb: 4 }}>
          <Typography variant="h6" color="primary.dark" gutterBottom>
            {title}
          </Typography>
          <Box sx={{ textAlign: "center", py: 6 }}>
            <CircularProgress />
            <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
              Fetching {title.toLowerCase()} advice...
            </Typography>
          </Box>
        </Paper>
      </Fade>
    );
  }

  if (error) {
    return (
      <Fade in timeout={300}>
        <Paper elevation={1} sx={{ p: 4, borderRadius: 3, mb: 4 }}>
          <Typography variant="h6" color="primary.dark" gutterBottom>
            {title}
          </Typography>
          <Alert severity="error">{error}</Alert>
        </Paper>
      </Fade>
    );
  }

  if (!result) return null;

  if (activeKey === "weather") {
    return (
      <Fade in timeout={300}>
        <Paper elevation={1} sx={{ p: 4, borderRadius: 3, mb: 4 }}>
          <Typography variant="h6" color="primary.dark" gutterBottom>
            Weather
          </Typography>
          <Box sx={{ display: "flex", alignItems: "center", gap: 3, flexWrap: "wrap" }}>
            <WbSunny sx={{ fontSize: 64, color: "#FB8C00" }} />
            <Box>
              <Typography variant="h2" sx={{ fontWeight: 900, lineHeight: 1 }}>
                {result.temp_c ?? result.temperature ?? "--"}&deg;C
              </Typography>
              <Typography variant="body1" color="text.secondary">
                {result.condition?.text ?? "Clear"} &middot; Humidity: {result.humidity ?? "--"}%
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Wind: {result.wind_kph ?? "--"} km/h &middot; Precipitation: {result.precip_mm ?? "--"} mm
              </Typography>
            </Box>
          </Box>
        </Paper>
      </Fade>
    );
  }

  const text = result.recommendation || result.alert || result.reminder || "";

  return (
    <Fade in timeout={300}>
      <Paper elevation={1} sx={{ p: 4, borderRadius: 3, mb: 4 }}>
        <Typography variant="h6" color="primary.dark" gutterBottom>
          {title}
        </Typography>
        <AdviceImage keywords={text.toLowerCase().match(/\b\w+\b/g) || []} activeKey={activeKey} />
        <Typography variant="body1" sx={{ whiteSpace: "pre-line", mb: 2 }}>
          {text}
        </Typography>
        <SmsStatus result={result} />
      </Paper>
    </Fade>
  );
}
