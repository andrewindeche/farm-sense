import { configureStore } from "@reduxjs/toolkit";
import authReducer from "./slices/authSlice";
import locationReducer from "./slices/locationSlice";
import adviceReducer from "./slices/adviceSlice";
import subscriberReducer from "./slices/subscriberSlice";

const store = configureStore({
  reducer: {
    auth: authReducer,
    location: locationReducer,
    advice: adviceReducer,
    subscribers: subscriberReducer,
  },
});

export default store;
