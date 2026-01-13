import { NextResponse } from "next/server";

export async function POST(request: Request) {
  const ENGINE_URL =
    process.env.ENGINE_URL || process.env.API_URL || "http://engine:8000";

  try {
    console.log(`PROXY_REQUEST: POST ${ENGINE_URL}/api/data/refresh`);

    const response = await fetch(`${ENGINE_URL}/api/data/refresh`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    });

    const data = await response.json();
    console.log(`PROXY_RESPONSE: ${response.status}`, data);

    if (!response.ok) {
      return NextResponse.json(
        { detail: data.detail || `Engine responded with ${response.status}` },
        { status: response.status }
      );
    }

    return NextResponse.json(data);
  } catch (error: any) {
    console.error("REFRESH_PROXY_ERROR:", error);
    return NextResponse.json(
      { detail: error.message || "Internal Server Error" },
      { status: 500 }
    );
  }
}
