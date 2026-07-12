export const isExhibitionDemoMode =
  String(import.meta.env.VITE_EXHIBITION_DEMO_MODE)
    .trim()
    .toLowerCase() === "true";

export const DEMO_STORAGE_KEYS = {
  portfolio: "finlight_exhibition_demo_portfolio",
  settings: "finlight_exhibition_demo_settings",
};
