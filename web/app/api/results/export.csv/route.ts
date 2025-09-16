import { NextRequest } from "next/server";

export async function GET(req: NextRequest) {
  const { searchParams } = new URL(req.url);
  const params = new URLSearchParams(searchParams);
  return fetch(`${process.env.NEXT_PUBLIC_API_URL}/results/export.csv?${params.toString()}`, {
    headers: { "Authorization": `Bearer ${localStorage.getItem('rb.jwt')}` },
  });
}
