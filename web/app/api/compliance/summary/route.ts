import { NextRequest, NextResponse } from "next/server";

export async function GET(req: NextRequest) {
  const { searchParams } = new URL(req.url);
  const framework = searchParams.get("framework");
  const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/compliance/summary?framework=${framework}`);
  const data = await res.json();
  return NextResponse.json(data, { status: res.status });
}
