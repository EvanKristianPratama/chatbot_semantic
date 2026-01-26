import { NextRequest, NextResponse } from 'next/server';

// Configuration for Python Backend
const PYTHON_BACKEND_URL = 'https://chatbot-semantic.vercel.app/chat';

export async function POST(req: NextRequest) {
    try {
        const body = await req.json();
        const { message } = body;

        if (!message) {
            return NextResponse.json(
                { error: 'Message is required' },
                { status: 400 }
            );
        }

        // Forward request to Python Semantic Backend
        console.log(`Forwarding to Semantic Backend: ${PYTHON_BACKEND_URL}`);

        try {
            const pythonResponse = await fetch(PYTHON_BACKEND_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message })
            });

            if (!pythonResponse.ok) {
                const errorText = await pythonResponse.text();
                console.error('Python Backend Error:', errorText);
                return NextResponse.json(
                    { error: `Semantic Backend Error: ${pythonResponse.status}` },
                    { status: 502 } // Bad Gateway
                );
            }

            const data = await pythonResponse.json();

            // Map Python response to Frontend expectation
            // Python returns { response: "...", debug_facts: [...] }
            // Frontend expects { success: true, da: "..." }
            return NextResponse.json({
                success: true,
                da: data.response,
                debug: data.debug_facts
            });

        } catch (fetchError) {
            console.error('Failed to connect to Python Backend:', fetchError);
            return NextResponse.json(
                { error: 'Connection to Semantic Backend failed. Is app.py running?' },
                { status: 503 } // Service Unavailable
            );
        }

    } catch (error) {
        console.error('API Route Error:', error);
        return NextResponse.json(
            { error: 'Internal Server Error' },
            { status: 500 }
        );
    }
}
