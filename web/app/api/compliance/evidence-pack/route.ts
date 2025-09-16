import { NextRequest } from "next/server";

export async function GET(req: NextRequest) {
  const { searchParams } = new URL(req.url);
  const framework = searchParams.get("framework");
  return fetch(`${process.env.NEXT_PUBLIC_API_URL}/compliance/evidence-pack?framework=${framework}`);
}
