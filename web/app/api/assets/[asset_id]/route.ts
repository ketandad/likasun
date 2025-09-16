import { NextRequest, NextResponse } from "next/server";

export async function GET(req: NextRequest) {
  const assetId = req.url.split("/api/assets/")[1].split("?")[0];
  const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/assets/${assetId}`, {
    headers: { "Authorization": `Bearer ${localStorage.getItem('rb.jwt')}` },
  });
  const data = await res.json();
  return NextResponse.json(data, { status: res.status });
}
