import { NextResponse } from "next/server";

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const source_id = searchParams.get("source_id");
  const target_id = searchParams.get("target_id");

  const ENGINE_URL = process.env.ENGINE_URL || "http://engine:8000";

  try {
    const response = await fetch(
      `${ENGINE_URL}/api/industries/available?source_id=${source_id}&target_id=${target_id}`,
      {
        method: "GET",
        headers: { "Content-Type": "application/json" },
        cache: "no-store",
      }
    );

    if (!response.ok) {
      throw new Error(`Engine responded with ${response.status}`);
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error: any) {
    console.error("AVAILABLE_INDUSTRIES_PROXY_ERROR:", error);
    return NextResponse.json({ detail: error.message }, { status: 500 });
  }
}
