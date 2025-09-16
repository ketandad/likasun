import { NextRequest, NextResponse } from "next/server";

export async function GET(req: NextRequest) {
  const runId = req.url.split("/api/evaluate/runs/")[1].split("?")[0];
  const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/evaluate/runs/${runId}`);
  const data = await res.json();
  return NextResponse.json(data, { status: res.status });
}
