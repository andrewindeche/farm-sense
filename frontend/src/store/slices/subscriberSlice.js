import { createSlice } from "@reduxjs/toolkit";

const subscriberSlice = createSlice({
  name: "subscribers",
  initialState: {
    list: [],
    loading: false,
    phone: "",
    subLat: -1.2921,
    subLon: 36.8219,
    subMsg: "",
    subMsgSeverity: "success",
    delivering: false,
    deliveryResult: null,
    editDialog: null,
  },
  reducers: {
    setList(state, action) {
      state.list = action.payload;
    },
    setLoading(state, action) {
      state.loading = action.payload;
    },
    setPhone(state, action) {
      state.phone = action.payload;
    },
    setSubLat(state, action) {
      state.subLat = action.payload;
    },
    setSubLon(state, action) {
      state.subLon = action.payload;
    },
    setSubMsg(state, action) {
      state.subMsg = action.payload.text;
      state.subMsgSeverity = action.payload.severity;
    },
    setDelivering(state, action) {
      state.delivering = action.payload;
    },
    setDeliveryResult(state, action) {
      state.deliveryResult = action.payload;
    },
    setEditDialog(state, action) {
      state.editDialog = action.payload;
    },
  },
});

export const {
  setList,
  setLoading,
  setPhone,
  setSubLat,
  setSubLon,
  setSubMsg,
  setDelivering,
  setDeliveryResult,
  setEditDialog,
} = subscriberSlice.actions;
export default subscriberSlice.reducer;
