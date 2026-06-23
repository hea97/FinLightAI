# FinLightAI Design System v2

## Purpose

FinLightAI is an AI market briefing dashboard, not an investment recommendation service or a landing page. The UI should feel compact, scannable, and data-oriented at browser zoom 100%.

This v2 system focuses on:

- Reducing oversized typography and KPI numbers by about 10-18%.
- Separating news impact from news trust.
- Keeping green, yellow, and red signal colors, but pairing every color with labels and numbers.
- Increasing dashboard density through smaller card padding and tighter spacing.

## Font System

```css
:root {
  --font-sans: "Pretendard", "Inter", "Noto Sans KR", "Segoe UI", Arial, sans-serif;
  --font-mono: "JetBrains Mono", "Cascadia Mono", "SFMono-Regular", Consolas, monospace;
}
```

Use `--font-sans` for general UI text. Use `--font-mono` or `font-variant-numeric: tabular-nums` for KPI values, scores, rates, and risk numbers.

## Typography Scale

| Token | Size | Weight | Usage |
| --- | ---: | ---: | --- |
| `--text-xs` | 11px | 500-700 | Helper text, units, chip labels |
| `--text-sm` | 12px | 500-700 | Small buttons, captions |
| `--text-md` | 14px | 500-700 | Body, card descriptions |
| `--text-lg` | 16px | 650-780 | Card titles, news titles |
| `--text-xl` | 20px | 700-800 | Section emphasis |
| `--text-2xl` | 24px | 750-850 | Page title |
| `--text-hero` | 28px | 800-850 | Main market signal sentence |
| `--text-kpi` | 32px | 800-850 | KPI numbers |
| `--text-signal` | 34px | 850 | Signal badge icon/value |

```css
:root {
  --text-xs: 0.6875rem;
  --text-sm: 0.75rem;
  --text-md: 0.875rem;
  --text-lg: 1rem;
  --text-xl: 1.25rem;
  --text-2xl: 1.5rem;
  --text-hero: 1.75rem;
  --text-kpi: 2rem;
  --text-signal: 2.125rem;
}
```

## Component Typography

| Component | Element | Recommended Size |
| --- | --- | ---: |
| Header | Brand text | 20px |
| Header | Page title | 22-24px |
| Header | Navigation buttons | 14px |
| Market signal | Card title | 16px |
| Market signal | Main sentence | 28px |
| Market signal | Description | 14px |
| KPI card | Label | 13px |
| KPI card | Value | 30-32px |
| KPI card | Caption | 12-13px |
| News TOP 5 | News title | 14-15px |
| News TOP 5 | Chip | 11-12px |
| Industry heatmap | Industry name | 14px |
| Industry heatmap | Score | 26-30px |

## Color Tokens

```css
:root {
  --color-bg: #080d14;
  --color-surface: #111722;
  --color-surface-2: #151c29;
  --color-surface-3: #1a2231;
  --color-card: rgba(18, 24, 36, 0.92);
  --color-border: rgba(148, 163, 184, 0.18);
  --color-border-strong: rgba(148, 163, 184, 0.30);

  --color-text-primary: #eef4ff;
  --color-text-secondary: #c2ccda;
  --color-text-muted: #8792a3;

  --color-green: #79d66f;
  --color-green-text: #9af28f;
  --color-yellow: #f4d34f;
  --color-yellow-text: #ffe77a;
  --color-red: #ef6b61;
  --color-red-text: #ff8e86;
  --color-blue: #7da2ff;
  --color-brand-mint: #8ee8d2;
}
```

## Signal Rules

| Signal | Score Range | Treatment |
| --- | ---: | --- |
| Strong positive | `+60` and above | Green gradient, score plus label |
| Mild positive | `+15` to `+59` | Muted green/teal |
| Neutral | `-14` to `+14` | Neutral card |
| Caution | `-15` to `-49` | Yellow/brown muted |
| Negative | `-50` and below | Red gradient |

Do not communicate state by color alone. Always include a numeric score and a text label.

## Spacing And Radius

| Component | Padding | Radius |
| --- | ---: | ---: |
| Page | `24px` horizontal | - |
| Header | `14-18px 24px` | - |
| Main panel | `20-24px` | `18-22px` |
| KPI card | `18px` | `14-16px` |
| News row | `10-12px 0` | - |
| Chip | `4px 8px` | `999px` |

## Dashboard Layout

Desktop layout:

```text
Today market signal     | AI briefing summary
Market KPI strip        | News impact TOP 5
Industry heatmap        | News Guard warning
                        | Recent Kakao alerts
```

Recommended grid:

```css
.dashboard {
  display: grid;
  grid-template-columns: minmax(0, 7fr) minmax(360px, 5fr);
  gap: 16px;
}
```

## Developer Notes

- Keep the current AI briefing dashboard direction.
- At 100% browser zoom, reduce the landing-page feeling by using 14px body text and 30-32px KPI numbers.
- Header, navigation, and CTA buttons should be real buttons with state transitions.
- Maintain separate tabs and data for domestic market, overseas market, and watched industries.
- Industry heatmap cards should move to or select the watched industry state when clicked.
- Avoid investment recommendation phrases such as buy, sell, guaranteed return, or certain profit.
