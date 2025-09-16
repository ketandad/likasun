import { NextRequest, NextResponse } from "next/server";

export async function GET(req: NextRequest) {
  const resultId = req.url.split("/api/results/")[1].split("?")[0];
  // resultId format: control_id:asset_id
  const [controlId, assetId] = resultId.split(":");
  const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/results/${controlId}/${assetId}`);
  const data = await res.json();
  return NextResponse.json(data, { status: res.status });
}
