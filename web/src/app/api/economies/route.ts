import { NextResponse } from 'next/server';

export async function GET() {
  const ENGINE_URL = process.env.ENGINE_URL || 'http://engine:8000';
  
  try {
    const response = await fetch(`${ENGINE_URL}/economies`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
      next: { revalidate: 3600 } // Cache for 1 hour
    });
    
    if (!response.ok) {
      throw new Error(`Engine responded with ${response.status}`);
    }
    
    const data = await response.json();
    return NextResponse.json(data);
  } catch (error: any) {
    console.error('ECONOMIES_PROXY_ERROR:', error);
    return NextResponse.json({ detail: error.message }, { status: 500 });
  }
}
