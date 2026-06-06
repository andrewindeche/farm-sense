import { Box, Typography } from "@mui/material";

export default function Footer() {
  return (
    <Box
      component="footer"
      sx={{
        bgcolor: "secondary.dark",
        color: "#fff",
        textAlign: "center",
        py: 2,
        mt: "auto",
      }}
    >
      <Typography variant="body2" sx={{ color: "#A5D6A7" }}>
        &copy; {new Date().getFullYear()} FarmSense — Empowering Farmers with
        Smart Advice
      </Typography>
    </Box>
  );
}
