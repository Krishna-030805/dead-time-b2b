import "./globals.css";

export const metadata = {
  title: "Dead Time — Workflow Intelligence",
  description:
    "Continuous workflow observation, pattern detection, ROI quantification, and AI-powered automation recommendations.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
