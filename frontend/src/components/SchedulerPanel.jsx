import { useCallback, useEffect, useMemo } from "react";
import {
  Box,
  Paper,
  Typography,
  Grid,
  TextField,
  Button,
  Alert,
  CircularProgress,
  Fade,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from "@mui/material";
import {
  Schedule,
  AddCircle,
  PlayArrow,
  Delete,
  Edit,
  People,
  CheckCircle,
} from "@mui/icons-material";
import { useSelector, useDispatch } from "react-redux";
import {
  setList,
  setLoading,
  setPhone,
  setSubLat,
  setSubLon,
  setSubMsg,
  setDelivering,
  setDeliveryResult,
  setEditDialog,
} from "../store/slices/subscriberSlice";

function SubscriberRow({ sub, onEdit, onDelete }) {
  return (
    <Paper
      variant="outlined"
      sx={{
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        p: 2,
        mb: 1,
      }}
    >
      <Box>
        <Typography variant="body2" fontWeight={600}>
          {sub.phone}
        </Typography>
        <Typography variant="caption" color="text.secondary">
          {sub.lat}, {sub.lon}
        </Typography>
      </Box>
      <Box sx={{ display: "flex", gap: 0.5 }}>
        <IconButton size="small" onClick={() => onEdit(sub)}>
          <Edit fontSize="small" />
        </IconButton>
        <IconButton size="small" color="error" onClick={() => onDelete(sub.phone)}>
          <Delete fontSize="small" />
        </IconButton>
      </Box>
    </Paper>
  );
}

function DeliveryResult({ result }) {
  if (!result) return null;
  return (
    <Fade in timeout={300}>
      <Box sx={{ mt: 2 }}>
        {result.error ? (
          <Alert severity="error">{result.error}</Alert>
        ) : (
          <Box
            sx={{
              p: 2,
              borderRadius: 2,
              bgcolor: "#E8F5E9",
              border: 1,
              borderColor: "#A5D6A7",
            }}
          >
            <Typography variant="subtitle2" color="success.dark">
              <CheckCircle
                fontSize="small"
                sx={{ verticalAlign: "middle", mr: 0.5 }}
              />
              Delivered to {result.delivered} of {result.total} subscribers
            </Typography>
            {result.results?.map((r, i) => (
              <Typography
                key={i}
                variant="caption"
                color="text.secondary"
                sx={{ display: "block", ml: 3, mt: 0.5 }}
              >
                {r.phone} &middot; SMS: {r.sms_status}
              </Typography>
            ))}
          </Box>
        )}
      </Box>
    </Fade>
  );
}

export default function SchedulerPanel() {
  const dispatch = useDispatch();
  const {
    list,
    loading,
    phone,
    subLat,
    subLon,
    subMsg,
    subMsgSeverity,
    delivering,
    deliveryResult,
    editDialog,
  } = useSelector((s) => s.subscribers);

  const fetchSubscribers = useCallback(async () => {
    dispatch(setLoading(true));
    try {
      const res = await fetch("/api/scheduler/subscribers");
      const data = await res.json();
      if (res.ok) dispatch(setList(data.subscribers || []));
    } catch { /* ignore */ }
    finally { dispatch(setLoading(false)); }
  }, [dispatch]);

  useEffect(() => { fetchSubscribers(); }, [fetchSubscribers]);

  const handleSubscribe = async (e) => {
    e.preventDefault();
    dispatch(setSubMsg({ text: "", severity: "success" }));
    if (!phone.trim()) {
      dispatch(setSubMsg({ text: "Phone number is required", severity: "error" }));
      return;
    }
    try {
      const res = await fetch("/api/scheduler/subscribe", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ phone: phone.trim(), lat: subLat, lon: subLon }),
      });
      const data = await res.json();
      if (!res.ok) {
        dispatch(setSubMsg({ text: data.detail || "Subscription failed", severity: "error" }));
        return;
      }
      dispatch(
        setSubMsg({
          text:
            data.status === "updated"
              ? "Subscriber updated successfully"
              : "Subscriber added successfully",
          severity: "success",
        }),
      );
      dispatch(setPhone(""));
      fetchSubscribers();
    } catch {
      dispatch(setSubMsg({ text: "Network error", severity: "error" }));
    }
  };

  const handleUnsubscribe = async (p) => {
    try {
      await fetch("/api/scheduler/unsubscribe", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ phone: p }),
      });
      fetchSubscribers();
    } catch { /* ignore */ }
  };

  const handleDeliverNow = async () => {
    dispatch(setDelivering(true));
    dispatch(setDeliveryResult(null));
    try {
      const res = await fetch("/api/scheduler/deliver-now", { method: "POST" });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Delivery failed");
      dispatch(setDeliveryResult(data));
    } catch (err) {
      dispatch(setDeliveryResult({ error: err.message }));
    } finally {
      dispatch(setDelivering(false));
    }
  };

  const handleEditSave = async () => {
    if (!editDialog) return;
    const { oldPhone, newPhone, lat, lon } = editDialog;
    try {
      if (newPhone !== oldPhone) {
        await fetch("/api/scheduler/unsubscribe", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ phone: oldPhone }),
        });
      }
      const res = await fetch("/api/scheduler/subscribe", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ phone: newPhone, lat, lon }),
      });
      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || "Update failed");
      }
      dispatch(setEditDialog(null));
      fetchSubscribers();
    } catch (err) {
      alert(err.message);
    }
  };

  const subscriberRows = useMemo(
    () =>
      list.map((sub) => (
        <SubscriberRow
          key={sub.phone}
          sub={sub}
          onEdit={(s) =>
            dispatch(
              setEditDialog({
                oldPhone: s.phone,
                newPhone: s.phone,
                lat: s.lat,
                lon: s.lon,
              }),
            )
          }
          onDelete={handleUnsubscribe}
        />
      )),
    [list, dispatch, handleUnsubscribe],
  );

  return (
    <>
      <Paper elevation={1} sx={{ p: 4, borderRadius: 3 }}>
        <Box sx={{ display: "flex", alignItems: "center", gap: 1, mb: 3 }}>
          <Schedule color="primary" />
          <Typography variant="h6" color="primary.dark">
            Scheduled Delivery
          </Typography>
        </Box>

        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          Manage daily SMS subscribers. Advice is delivered automatically at{" "}
          <strong>6:00 AM</strong> every day.
        </Typography>

        <Grid container spacing={4}>
          <Grid size={{ xs: 12, md: 5 }}>
            <Typography variant="subtitle2" color="primary.dark" gutterBottom>
              Add Subscriber
            </Typography>
            <Box
              component="form"
              onSubmit={handleSubscribe}
              sx={{ display: "flex", flexDirection: "column", gap: 2 }}
            >
              <TextField
                label="Phone number"
                placeholder="+254712345678"
                size="small"
                value={phone}
                onChange={(e) => dispatch(setPhone(e.target.value))}
              />
              <Box sx={{ display: "flex", gap: 2 }}>
                <TextField
                  label="Latitude"
                  type="number"
                  size="small"
                  value={subLat}
                  onChange={(e) =>
                    dispatch(setSubLat(parseFloat(e.target.value) || 0))
                  }
                  sx={{ maxWidth: 140 }}
                />
                <TextField
                  label="Longitude"
                  type="number"
                  size="small"
                  value={subLon}
                  onChange={(e) =>
                    dispatch(setSubLon(parseFloat(e.target.value) || 0))
                  }
                  sx={{ maxWidth: 140 }}
                />
              </Box>
              <Button
                type="submit"
                variant="contained"
                startIcon={<AddCircle />}
                sx={{ alignSelf: "flex-start" }}
              >
                Add Subscriber
              </Button>
              {subMsg && (
                <Alert severity={subMsgSeverity} sx={{ py: 0.5 }}>
                  {subMsg}
                </Alert>
              )}
            </Box>

            <Box sx={{ mt: 3 }}>
              <Button
                variant="outlined"
                color="secondary"
                startIcon={<PlayArrow />}
                onClick={handleDeliverNow}
                disabled={delivering}
                fullWidth
              >
                {delivering ? "Delivering..." : "Deliver Now"}
              </Button>
            </Box>

            <DeliveryResult result={deliveryResult} />
          </Grid>

          <Grid size={{ xs: 12, md: 7 }}>
            <Box
              sx={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                mb: 1,
              }}
            >
              <Typography variant="subtitle2" color="primary.dark">
                Subscribers ({list.length})
              </Typography>
              {loading && <CircularProgress size={16} />}
              {!loading && (
                <Button size="small" onClick={fetchSubscribers}>
                  Refresh
                </Button>
              )}
            </Box>

            {list.length === 0 && !loading && (
              <Paper
                variant="outlined"
                sx={{ p: 4, textAlign: "center", bgcolor: "#FAFAFA" }}
              >
                <People sx={{ fontSize: 40, color: "#C8E6C9", mb: 1 }} />
                <Typography variant="body2" color="text.secondary">
                  No subscribers yet. Add one to start daily deliveries.
                </Typography>
              </Paper>
            )}

            {subscriberRows}
          </Grid>
        </Grid>
      </Paper>

      <Dialog
        open={!!editDialog}
        onClose={() => dispatch(setEditDialog(null))}
        maxWidth="xs"
        fullWidth
      >
        <DialogTitle>Edit Subscriber</DialogTitle>
        <DialogContent>
          {editDialog && (
            <Box sx={{ display: "flex", flexDirection: "column", gap: 2, pt: 1 }}>
              <TextField
                label="Phone number"
                size="small"
                value={editDialog.newPhone}
                onChange={(e) =>
                  dispatch(setEditDialog({ ...editDialog, newPhone: e.target.value }))
                }
              />
              <Box sx={{ display: "flex", gap: 2 }}>
                <TextField
                  label="Latitude"
                  type="number"
                  size="small"
                  value={editDialog.lat}
                  onChange={(e) =>
                    dispatch(
                      setEditDialog({
                        ...editDialog,
                        lat: parseFloat(e.target.value) || 0,
                      }),
                    )
                  }
                />
                <TextField
                  label="Longitude"
                  type="number"
                  size="small"
                  value={editDialog.lon}
                  onChange={(e) =>
                    dispatch(
                      setEditDialog({
                        ...editDialog,
                        lon: parseFloat(e.target.value) || 0,
                      }),
                    )
                  }
                />
              </Box>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => dispatch(setEditDialog(null))}>Cancel</Button>
          <Button variant="contained" onClick={handleEditSave}>
            Save
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}
