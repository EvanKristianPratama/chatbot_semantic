export interface Product {
    id: string;
    store_name: string;
    listing_title: string;
    price_idr: number;
    stock: number;
    item_condition: string;
}

export interface ApiResponse {
    success: boolean;
    data?: Product[];
    message?: string;
}

// Configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function searchProducts(query: string): Promise<ApiResponse> {
    try {
        const response = await fetch(`${API_BASE_URL}/api_market.php?search=${encodeURIComponent(query)}`);

        if (!response.ok) {
            throw new Error(`API Error: ${response.statusText}`);
        }

        const data = await response.json();
        return { success: true, data };
    } catch (error) {
        console.error('Failed to fetch products:', error);
        return {
            success: false,
            message: error instanceof Error ? error.message : 'Unknown error'
        };
    }
}
