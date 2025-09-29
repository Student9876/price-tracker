'use client';

import { Inter } from "next/font/google";
import "./globals.css";
import StoreProvider from "@/lib/StoreProvider";
import { useEffect } from "react";
import { useDispatch } from "react-redux";
import { checkAuth } from "@/lib/authSlice";

const inter = Inter({ subsets: ["latin"] });

function AppInitializer({ children }) {
  const dispatch = useDispatch();
  useEffect(() => {
    dispatch(checkAuth());
  }, [dispatch]);
  return <>{children}</>;
}

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <StoreProvider>
          <AppInitializer>
            {children}
          </AppInitializer>
        </StoreProvider>
      </body>
    </html>
  );
}