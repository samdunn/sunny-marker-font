import localFont from "next/font/local";

export const SunnyMarker = localFont({
  src: [
    { path: "./files/SunnyMarker-Variable.woff2", style: "normal" },
    { path: "./files/SunnyMarker-Variable.woff2", style: "oblique 0deg 9deg" },
  ],
  weight: "300 700",
  display: "swap",
  variable: "--font-sunny-marker",
  preload: false,
  declarations: [{ prop: "font-stretch", value: "75% 125%" }],
});
