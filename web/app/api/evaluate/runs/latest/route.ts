import { NextRequest, NextResponse } from "next/server";

export async function GET() {
  const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/evaluate/runs/latest`, {
    method: "GET",
    headers: { "Authorization": `Bearer ${localStorage.getItem('rb.jwt')}` },
  });
  const data = await res.json();
  return NextResponse.json(data, { status: res.status });
}
