import type { DataSource } from "./dataSource";
import { mockSource } from "./mock";

/** The single door to all data. Pages import this, never an adapter. */
export const api: DataSource = mockSource;
