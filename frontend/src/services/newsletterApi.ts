import { apiFetch } from "./apiClient";

export type EmailSubscription = {
  email: string | null;
  status: "inactive" | "active";
  consentedAt: string | null;
};

export function fetchEmailSubscription(): Promise<EmailSubscription> {
  return apiFetch("/api/email-subscription");
}

export function saveEmailSubscription(email: string): Promise<EmailSubscription> {
  return apiFetch("/api/email-subscription", {
    method: "PUT",
    body: JSON.stringify({ email, consent: true }),
  });
}
