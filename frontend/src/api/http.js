import axios from "axios";

import { getAccessToken } from "../utils/session";

const http = axios.create({
  baseURL: "/api",
  timeout: 10000,
});

http.interceptors.request.use((config) => {
  const token = getAccessToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default http;
