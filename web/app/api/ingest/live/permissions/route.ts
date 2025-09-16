import { NextRequest, NextResponse } from "next/server";

export async function GET(req: NextRequest) {
  const { searchParams } = new URL(req.url);
  const cloud = searchParams.get("cloud");
  const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/ingest/live/permissions?cloud=${cloud}`);
  const data = await res.json();
  return NextResponse.json(data, { status: res.status });
}
