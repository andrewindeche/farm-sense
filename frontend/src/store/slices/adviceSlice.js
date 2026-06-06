import { createSlice } from "@reduxjs/toolkit";

const adviceSlice = createSlice({
  name: "advice",
  initialState: { activeKey: null, result: null, loading: false, error: "" },
  reducers: {
    fetchStart(state, action) {
      state.activeKey = action.payload;
      state.loading = true;
      state.error = "";
      state.result = null;
    },
    fetchSuccess(state, action) {
      state.loading = false;
      state.result = action.payload;
    },
    fetchFail(state, action) {
      state.loading = false;
      state.error = action.payload;
    },
    clearAdvice(state) {
      state.activeKey = null;
      state.result = null;
      state.loading = false;
      state.error = "";
    },
  },
});

export const { fetchStart, fetchSuccess, fetchFail, clearAdvice } =
  adviceSlice.actions;
export default adviceSlice.reducer;
