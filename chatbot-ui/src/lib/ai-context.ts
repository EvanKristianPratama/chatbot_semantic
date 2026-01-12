// AI Context Management for GadgetBot
// Ensures AI stays focused on smartphone/gadget topics

export const SYSTEM_PROMPT = `# GadgetBot System Prompt

## Identity
Kamu adalah **GadgetBot**, asisten AI cerdas yang HANYA membahas tentang smartphone dan gadget. Kamu SANGAT menguasai:
- Spesifikasi teknis smartphone (RAM, Storage, Processor, Layar)
- Harga pasar smartphone di Indonesia
- Perbandingan antar brand dan model
- Rekomendasi berdasarkan kebutuhan user

## Strict Boundaries
⛔ JANGAN PERNAH membahas:
- Politik, agama, SARA
- Topik sensitif atau kontroversial
- Hal-hal di luar smartphone/gadget
- Memberikan saran medis/hukum/finansial

Jika user bertanya di luar topik, jawab dengan sopan:
"Maaf, saya hanya bisa membantu seputar smartphone dan gadget. Ada yang ingin ditanyakan tentang HP? 📱"

## Response Guidelines
1. Selalu gunakan emoji yang relevan 📱💰🔋
2. Format harga dalam Rupiah (Rp X.XXX.XXX)
3. Berikan maksimal 3-5 rekomendasi per query
4. Sertakan alasan di balik setiap rekomendasi
5. Tanyakan preferensi user jika query ambigu

## Context Memory
Ingat preferensi user dalam conversation:
- Brand favorit yang disebutkan
- Budget yang ditetapkan
- Kebutuhan spesifik (gaming, fotografi, dll)

## Knowledge Base
Database smartphone yang tersedia:
- Samsung: Galaxy S24, Galaxy S23 Ultra, Galaxy A05s
- Apple: iPhone 15, iPhone 15 Pro Max
- Xiaomi: Poco F5, Poco X6 Pro, Redmi Note 13 Pro+
- Lainnya: Vivo V30, Realme C67, ROG Phone 8, Tecno Pova 6, Infinix GT 20 Pro

## Response Format
Untuk rekomendasi produk, gunakan format:

📱 **[Nama HP]** ([Kondisi])
⚙️ Spek: RAM [X]GB, [Processor]
💰 Harga: Rp [X,XXX,XXX]
🏪 Toko: [Nama Toko]
`;

// Blocked topics and keywords
const BLOCKED_TOPICS = [
    'politik', 'agama', 'sara', 'hack', 'crack',
    'bypass', 'illegal', 'xxx', 'drugs', 'narkoba',
    'judi', 'gambling', 'teroris', 'bunuh',
];

const GADGET_KEYWORDS = [
    'smartphone', 'hp', 'handphone', 'ponsel', 'gadget',
    'ram', 'processor', 'prosesor', 'harga', 'rupiah',
    'samsung', 'apple', 'iphone', 'xiaomi', 'oppo', 'vivo',
    'realme', 'poco', 'redmi', 'asus', 'rog', 'infinix',
    'tecno', 'gaming', 'kamera', 'baterai', 'layar',
    'storage', 'memori', 'spek', 'spesifikasi',
    'flagship', 'budget', 'murah', 'mahal', 'mid-range',
];

export interface ContentFilterResult {
    isAllowed: boolean;
    reason?: string;
}

export function validateUserInput(message: string): ContentFilterResult {
    const lowerMessage = message.toLowerCase();

    // Check for blocked topics
    for (const topic of BLOCKED_TOPICS) {
        if (lowerMessage.includes(topic)) {
            return {
                isAllowed: false,
                reason: `Topik "${topic}" tidak diizinkan`,
            };
        }
    }

    return { isAllowed: true };
}

export function validateAIResponse(response: string): ContentFilterResult {
    const lowerResponse = response.toLowerCase();

    // Check if response contains gadget-related content
    const hasGadgetContext = GADGET_KEYWORDS.some(keyword =>
        lowerResponse.includes(keyword)
    );

    // Allow if has gadget context or is a polite deflection
    if (hasGadgetContext || lowerResponse.includes('smartphone dan gadget')) {
        return { isAllowed: true };
    }

    // Check for blocked content in AI response
    for (const topic of BLOCKED_TOPICS) {
        if (lowerResponse.includes(topic)) {
            return {
                isAllowed: false,
                reason: 'Response contains blocked content',
            };
        }
    }

    return { isAllowed: true };
}

// Safe response when content is blocked
export const SAFE_RESPONSE =
    'Maaf, saya hanya bisa membantu seputar smartphone dan gadget. Ada yang ingin ditanyakan tentang HP? 📱';

// Intent detection for analytics
export type QueryIntent =
    | 'brand_search'
    | 'price_filter'
    | 'spec_query'
    | 'gaming_search'
    | 'comparison'
    | 'general_help'
    | 'off_topic';

export function detectIntent(message: string): QueryIntent {
    const lowerMessage = message.toLowerCase();

    // Brand search
    const brands = ['samsung', 'apple', 'iphone', 'xiaomi', 'poco', 'redmi', 'oppo', 'vivo', 'realme', 'asus', 'rog', 'infinix', 'tecno'];
    if (brands.some(brand => lowerMessage.includes(brand))) {
        return 'brand_search';
    }

    // Price filter
    if (lowerMessage.includes('murah') || lowerMessage.includes('budget') ||
        lowerMessage.includes('juta') || lowerMessage.includes('harga')) {
        return 'price_filter';
    }

    // Spec query
    if (lowerMessage.includes('ram') || lowerMessage.includes('processor') ||
        lowerMessage.includes('storage') || lowerMessage.includes('kamera')) {
        return 'spec_query';
    }

    // Gaming search
    if (lowerMessage.includes('gaming') || lowerMessage.includes('game')) {
        return 'gaming_search';
    }

    // Comparison
    if (lowerMessage.includes('banding') || lowerMessage.includes('vs') ||
        lowerMessage.includes('lebih baik')) {
        return 'comparison';
    }

    // Check for off-topic
    const offTopicKeywords = ['cuaca', 'berita', 'resep', 'film', 'musik'];
    if (offTopicKeywords.some(keyword => lowerMessage.includes(keyword))) {
        return 'off_topic';
    }

    return 'general_help';
}

// Extract parameters from user message
export function extractParams(message: string): {
    brand?: string;
    minRam?: number;
    maxPrice?: number;
} {
    const lowerMessage = message.toLowerCase();
    const params: { brand?: string; minRam?: number; maxPrice?: number } = {};

    // Extract brand
    const brandMap: Record<string, string> = {
        'samsung': 'Samsung',
        'apple': 'Apple',
        'iphone': 'Apple',
        'xiaomi': 'Xiaomi',
        'poco': 'Poco',
        'redmi': 'Xiaomi',
        'oppo': 'Oppo',
        'vivo': 'Vivo',
        'realme': 'Realme',
        'asus': 'Asus',
        'rog': 'Asus',
        'infinix': 'Infinix',
        'tecno': 'Tecno',
    };

    for (const [keyword, brand] of Object.entries(brandMap)) {
        if (lowerMessage.includes(keyword)) {
            params.brand = brand;
            break;
        }
    }

    // Extract RAM requirement
    if (lowerMessage.includes('gaming') || lowerMessage.includes('berat')) {
        params.minRam = 12;
    } else if (lowerMessage.includes('standar')) {
        params.minRam = 4;
    }

    // Extract price
    const priceMatch = lowerMessage.match(/(\d+)\s*juta/);
    if (priceMatch) {
        params.maxPrice = parseInt(priceMatch[1]) * 1000000;
    } else if (lowerMessage.includes('murah') || lowerMessage.includes('budget')) {
        params.maxPrice = 7000000;
    }

    return params;
}
