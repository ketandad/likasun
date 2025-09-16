import { NextRequest, NextResponse } from "next/server";

export async function POST(req: NextRequest) {
  const { searchParams } = new URL(req.url);
  const cloud = searchParams.get("cloud");
  const uploadIds = searchParams.getAll("upload_id");
  const params = new URLSearchParams();
  params.set("cloud", cloud || "");
  uploadIds.forEach(id => params.append("upload_id", id));
  const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/ingest/parse?${params.toString()}`, {
    method: "POST",
    headers: { "Authorization": `Bearer ${localStorage.getItem('rb.jwt')}` },
  });
  const data = await res.json();
  return NextResponse.json(data, { status: res.status });
}
