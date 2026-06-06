import { AppBar, Toolbar, Typography, Button, Box } from "@mui/material";
import { Spa } from "@mui/icons-material";
import { useNavigate } from "react-router-dom";

export default function Header() {
  const navigate = useNavigate();
  const token = localStorage.getItem("token");

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("username");
    navigate("/login");
  };

  return (
    <AppBar position="sticky" sx={{ bgcolor: "primary.dark" }}>
      <Toolbar>
        <Spa sx={{ mr: 1, color: "#A5D6A7" }} />
        <Typography variant="h6" sx={{ flexGrow: 1, color: "#fff" }}>
          FarmSense
        </Typography>
        {token && (
          <Box sx={{ display: "flex", gap: 2, alignItems: "center" }}>
            <Typography variant="body2" sx={{ color: "#A5D6A7" }}>
              {localStorage.getItem("username")}
            </Typography>
            <Button
              variant="outlined"
              size="small"
              onClick={handleLogout}
              sx={{ borderColor: "#A5D6A7", color: "#fff" }}
            >
              Logout
            </Button>
          </Box>
        )}
      </Toolbar>
    </AppBar>
  );
}
