'use client';

import { useState, useCallback, useEffect } from 'react';
import { Message } from '@/types';
import { generateId } from '@/lib/utils';
import { searchProducts } from '@/lib/api';

// Set to true to use Real PHP API, false for Simulation
const USE_REAL_API = false;

interface UseChatOptions {
    onSend?: (message: string) => Promise<string>;
}

export function useChat(options?: UseChatOptions) {
    const [messages, setMessages] = useState<Message[]>([]);

    useEffect(() => {
        setMessages([
            {
                id: 'welcome',
                role: 'bot',
                content: '👋 Halo! Saya **GadgetBot**.\n\nSilakan tanya seputar smartphone, spesifikasi, atau rekomendasi harga.',
                timestamp: new Date(),
                type: 'text',
            }
        ]);
    }, []);
    const [isLoading, setIsLoading] = useState(false);
    const [inputValue, setInputValue] = useState('');

    const sendMessage = useCallback(async (content: string) => {
        if (!content.trim()) return;

        // Add user message
        const userMessage: Message = {
            id: generateId(),
            role: 'user',
            content: content.trim(),
            timestamp: new Date(),
            type: 'text',
        };

        setMessages(prev => [...prev, userMessage]);
        setInputValue('');
        setIsLoading(true);

        try {
            let botResponse: string;

            if (options?.onSend) {
                botResponse = await options.onSend(content);
            } else {
                botResponse = await getBotResponse(content);
            }

            const botMessage: Message = {
                id: generateId(),
                role: 'bot',
                content: botResponse,
                timestamp: new Date(),
                type: 'text',
            };

            setMessages(prev => [...prev, botMessage]);
        } catch (error) {
            console.error('Error sending message:', error);
            const errorMessage: Message = {
                id: generateId(),
                role: 'bot',
                content: '❌ Maaf, terjadi kesalahan. Silakan coba lagi.',
                timestamp: new Date(),
                type: 'text',
            };
            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setIsLoading(false);
        }
    }, [options]);

    const clearMessages = useCallback(() => {
        setMessages([{
            id: 'welcome',
            role: 'bot',
            content: '👋 Halo! Saya **GadgetBot**.\n\nSilakan tanya seputar smartphone, spesifikasi, atau rekomendasi harga.',
            timestamp: new Date(),
            type: 'text',
        }]);
    }, []);

    return {
        messages,
        isLoading,
        inputValue,
        setInputValue,
        sendMessage,
        clearMessages,
    };
}

// Logic to switch between Real API, Gemini, and Simulation
async function getBotResponse(userInput: string): Promise<string> {
    // 1. Try Gemini first (if configured)
    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: userInput }),
        });

        if (response.ok) {
            const data = await response.json();
            // Note: The API route returns { success: true, da: text } based on my previous code
            // But standard practice is data.text or data.response. Let's align with the route code: "da: text"
            if (data.da) return data.da;
            if (data.error) console.warn('Gemini Error:', data.error);
        }
    } catch (e) {
        console.warn('Gemini API Unavailable, falling back...', e);
    }

    // 2. Fallback to PHP API (if enabled)
    if (USE_REAL_API) {
        try {
            const response = await searchProducts(userInput);
            if (response.success && response.data && response.data.length > 0) {
                const productList = response.data.map(p =>
                    `📱 **${p.listing_title}**\n💰 Rp ${p.price_idr.toLocaleString('id-ID')}\n🏪 ${p.store_name}\n📦 Kondisi: ${p.item_condition}`
                ).join('\n\n');
                return `🔍 **Ditemukan ${response.data.length} produk di Database:**\n\n${productList}`;
            }
        } catch (error) {
            // Ignore and fallthrough to simulation
        }
    }

    // 3. Last Resort: Simulation
    return simulateAIResponse(userInput);
}

// Simulate AI response based on user input (Fallback)
async function simulateAIResponse(userMessage: string): Promise<string> {
    await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 1000));

    const lowerMessage = userMessage.toLowerCase();

    // Detect intent and respond accordingly
    if (lowerMessage.includes('samsung')) {
        return `🔍 **Hasil Pencarian Samsung (Simulasi):**

📱 **Galaxy S24** (Baru)
⚙️ Spek: RAM 8GB, Exynos 2400
💰 Harga: Rp 12.999.000
🏪 Toko: GadgetStore Official

📱 **Galaxy S23 Ultra** (Baru)
⚙️ Spek: RAM 12GB, Snapdragon 8 Gen 2
💰 Harga: Rp 15.499.000
🏪 Toko: Samsung Authorized

📱 **Galaxy A05s** (Baru)
⚙️ Spek: RAM 6GB, Snapdragon 680
💰 Harga: Rp 1.899.000
🏪 Toko: Budget Phone Shop

Ada yang ingin ditanyakan lebih lanjut tentang HP Samsung ini? 🤔`;
    }

    if (lowerMessage.includes('apple') || lowerMessage.includes('iphone')) {
        return `🔍 **Hasil Pencarian Apple (Simulasi):**

📱 **iPhone 15 Pro Max** (Baru)
⚙️ Spek: RAM 8GB, A17 Pro
💰 Harga: Rp 23.999.000
🏪 Toko: iBox Indonesia

📱 **iPhone 15** (Baru)
⚙️ Spek: RAM 6GB, A16 Bionic
💰 Harga: Rp 15.999.000
🏪 Toko: Apple Premium Reseller

Mau saya bandingkan dengan HP lain? 📊`;
    }

    if (lowerMessage.includes('gaming') || lowerMessage.includes('game')) {
        return `🎮 **Rekomendasi HP Gaming (Simulasi):**

📱 **ROG Phone 8** (Gaming)
⚙️ Spek: RAM 16GB, Snapdragon 8 Gen 3
💰 Harga: Rp 14.999.000
🏪 Toko: Asus Official Store
🔥 Performa: Beast Mode!

📱 **Poco X6 Pro** (Gaming Budget)
⚙️ Spek: RAM 12GB, Dimensity 8300 Ultra
💰 Harga: Rp 4.999.000
🏪 Toko: Xiaomi Indonesia

📱 **Galaxy S23 Ultra** (Flagship Gaming)
⚙️ Spek: RAM 12GB, Snapdragon 8 Gen 2
💰 Harga: Rp 15.499.000
🏪 Toko: Samsung Official

Semua HP di atas cocok untuk gaming berat! 🎯`;
    }

    if (lowerMessage.includes('murah') || lowerMessage.includes('budget')) {
        return `💰 **HP Budget Under 5 Juta (Simulasi):**

📱 **Realme C67** (Budget King)
⚙️ Spek: RAM 8GB, Snapdragon 685
💰 Harga: Rp 2.499.000
🏪 Toko: Realme Official

📱 **Galaxy A05s** (Samsung Murah)
⚙️ Spek: RAM 6GB, Snapdragon 680
💰 Harga: Rp 1.899.000
🏪 Toko: Samsung Authorized

📱 **Tecno Pova 6** (Baterai Monster)
⚙️ Spek: RAM 12GB, Helio G99 Ultimate
💰 Harga: Rp 2.799.000
🏪 Toko: Tecno Indonesia

Semua pilihan bagus untuk budget terbatas! 👍`;
    }

    if (lowerMessage.includes('xiaomi') || lowerMessage.includes('poco') || lowerMessage.includes('redmi')) {
        return `🔍 **Hasil Pencarian Xiaomi (Simulasi):**

📱 **Poco F5** (Flagship Killer)
⚙️ Spek: RAM 12GB, Snapdragon 7+ Gen 2
💰 Harga: Rp 5.299.000
🏪 Toko: Xiaomi Official

📱 **Redmi Note 13 Pro+ 5G** (Mid-Range King)
⚙️ Spek: RAM 12GB, Dimensity 7200 Ultra
💰 Harga: Rp 4.599.000
🏪 Toko: Mi Store

📱 **Poco X6 Pro** (Gaming Beast)
⚙️ Spek: RAM 12GB, Dimensity 8300 Ultra
💰 Harga: Rp 4.999.000
🏪 Toko: Poco Official

Value for money terbaik! 💪`;
    }

    // Check for off-topic queries
    const offTopicKeywords = ['politik', 'agama', 'resep', 'cuaca', 'berita'];
    if (offTopicKeywords.some(keyword => lowerMessage.includes(keyword))) {
        return `Maaf, saya hanya bisa membantu seputar smartphone dan gadget. Ada yang ingin ditanyakan tentang HP? 📱`;
    }

    // Generic helpful response
    return `Saya mengerti Anda mencari informasi tentang smartphone! 📱

Untuk hasil yang lebih akurat, coba sebutkan:
- **Brand**: Samsung, Apple, Xiaomi, dll
- **Kebutuhan**: Gaming, Fotografi, Harian
- **Budget**: Murah, Mid-range, Flagship

Contoh: "HP Samsung untuk gaming budget 5 juta"

Silakan coba lagi! 😊`;
}
