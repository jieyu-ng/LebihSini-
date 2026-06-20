import "./globals.css";

export const metadata = {
  title: "LebihSini GreenProof",
  description: "Reuse-first procurement intelligence",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-slate-50 text-slate-900">
        <main className="max-w-md mx-auto min-h-screen">
          {children}
        </main>
      </body>
    </html>
  );
}