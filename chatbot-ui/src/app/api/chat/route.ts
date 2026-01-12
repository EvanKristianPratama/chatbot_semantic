import { NextRequest, NextResponse } from 'next/server';

// Initialize Groq API Key
const apiKey = process.env.GROQ_API_KEY || '';

export async function POST(req: NextRequest) {
    try {
        console.log('API Request received (Groq)');

        if (!apiKey) {
            console.error('SERVER ERROR: GROQ_API_KEY is missing');
            return NextResponse.json(
                { error: 'API Key not configured on server' },
                { status: 500 }
            );
        }

        const body = await req.json();
        const { message } = body;

        if (!message) {
            return NextResponse.json(
                { error: 'Message is required' },
                { status: 400 }
            );
        }

        // System Prompt
        const systemPrompt = `
You are GadgetBot, an expert smartphone assistant.
Your goal is to help users find the best smartphones based on their needs (gaming, camera, budget, etc.).
Answer in Indonesian (Bahasa Indonesia).
Be helpful, concise, and friendly.
Use emojis sparingly to make the text lively.
Formatting: Use Markdown (bold, lists) for readability.

Context: 
- If user asks about price, give a realistic estimate in IDR (Rupiah).
- If user asks for recommendations, provide 2-3 options with pros/cons.
- If user talks about non-tech topics, politely steer back to gadgets.
`;

        // Call Groq API via Fetch (REST)
        const response = await fetch('https://api.groq.com/openai/v1/chat/completions', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${apiKey}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                messages: [
                    { role: 'system', content: systemPrompt },
                    { role: 'user', content: message }
                ],
                model: 'llama-3.3-70b-versatile', // Newest stable model
                temperature: 0.7,
                max_tokens: 1024
            })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(`Groq API Error: ${response.status} - ${JSON.stringify(errorData)}`);
        }

        const data = await response.json();
        const text = data.choices[0]?.message?.content || '';

        return NextResponse.json({ success: true, da: text });

    } catch (error) {
        console.error('Chat API Error:', error);
        return NextResponse.json(
            { error: 'Failed to process request with Groq AI' },
            { status: 500 }
        );
    }
}
