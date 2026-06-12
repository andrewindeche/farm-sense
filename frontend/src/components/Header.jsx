import { AppBar, Toolbar, Typography, Button, Box } from "@mui/material";
import { Spa } from "@mui/icons-material";
import { useNavigate } from "react-router-dom";
import { useSelector, useDispatch } from "react-redux";
import { logout } from "../store/slices/authSlice";

export default function Header() {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const { token, username } = useSelector((s) => s.auth);

  const handleLogout = () => {
    dispatch(logout());
    navigate("/login");
  };

  return (
    <AppBar position="sticky" sx={{ bgcolor: "primary.dark", zIndex: 1300 }}>
      <Toolbar>
        <Spa sx={{ mr: 1, color: "#A5D6A7" }} />
        <Typography variant="h6" sx={{ flexGrow: 1, color: "#fff" }}>
          FarmSense
        </Typography>
        {token && (
          <Box sx={{ display: "flex", gap: 2, alignItems: "center" }}>
            <Typography variant="body2" sx={{ color: "#A5D6A7" }}>
              {username}
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
