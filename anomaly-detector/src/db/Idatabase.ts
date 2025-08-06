import { Alert } from "../types/Alert.js";

export interface IDatabaseService {
  init(): Promise<void>;
  close(): Promise<void>;
  insertAlert(alert: Alert): Promise<void>;
}