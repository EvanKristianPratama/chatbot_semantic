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
        const systemPrompt = `Role:GadgetBot|Expert:Smartphone|Lang:ID|Style:Friendly,Professional,Clean,Concise,NoEmoji|Fmt:Markdown Lists(Bullets),Bold Names,No Tables,No Links|Content:Recs 2-3 options(Pros/Cons),Price(IDR)`;

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
                model: 'qwen/qwen3-32b', // Newest stable model
                temperature: 0.4,
                max_tokens: 4096
            })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(`Groq API Error: ${response.status} - ${JSON.stringify(errorData)}`);
        }

        const data = await response.json();
        let text = data.choices[0]?.message?.content || '';

        // Remove reasoning part (<think>...</think>) if present
        text = text.replace(/<think>[\s\S]*?<\/think>/g, '').trim();

        return NextResponse.json({ success: true, da: text });

    } catch (error) {
        console.error('Chat API Error:', error);
        return NextResponse.json(
            { error: 'Failed to process request with Groq AI' },
            { status: 500 }
        );
    }
}
