"use client";

import { api } from "../lib/api";
import { ApiStatus } from "./ui";

export default function Status() {
  return <ApiStatus check={() => api.health()} />;
}
