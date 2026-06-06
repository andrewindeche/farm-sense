import { createTheme } from "@mui/material";

const theme = createTheme({
  palette: {
    primary: { main: "#2E7D32", light: "#4CAF50", dark: "#1B5E20" },
    secondary: { main: "#5D4037", light: "#795548", dark: "#3E2723" },
    background: { default: "#FAFAFA", paper: "#FFFFFF" },
    text: { primary: "#1B5E20", secondary: "#5D4037" },
  },
  typography: {
    fontFamily: '"Lato", "Roboto", "Helvetica", "Arial", sans-serif',
    h4: { fontWeight: 700 },
    h5: { fontWeight: 600 },
    h6: { fontWeight: 600 },
  },
  shape: { borderRadius: 12 },
  components: {
    MuiButton: {
      styleOverrides: {
        root: { textTransform: "none", fontWeight: 600, borderRadius: 8 },
      },
    },
    MuiTextField: {
      defaultProps: { variant: "outlined", fullWidth: true },
    },
    MuiCard: {
      styleOverrides: { root: { boxShadow: "0 2px 12px rgba(0,0,0,0.08)" } },
    },
  },
});

export default theme;
