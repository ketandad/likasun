import { NextRequest, NextResponse } from "next/server";

export async function GET(req: NextRequest) {
  const { searchParams } = new URL(req.url);
  const params = new URLSearchParams(searchParams);
  const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/rules?${params.toString()}`, {
    headers: { "Authorization": `Bearer ${localStorage.getItem('rb.jwt')}` },
  });
  const data = await res.json();
  return NextResponse.json(data, { status: res.status });
}
