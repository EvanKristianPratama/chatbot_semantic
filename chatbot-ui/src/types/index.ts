// Types for GadgetBot Chatbot UI

export interface Message {
  id: string;
  role: 'user' | 'bot';
  content: string;
  timestamp: Date;
  type: 'text' | 'voice' | 'product' | 'image-gallery';
  productCard?: ProductCard;
  imageGallery?: string[];
  voiceDuration?: number;
}

export interface ProductCard {
  title: string;
  description: string;
  stats: ProductStat[];
  images?: string[];
}

export interface ProductStat {
  icon: string;
  value: string;
  label: string;
}

export interface Conversation {
  id: string;
  name: string;
  avatar?: string;
  lastMessage: string;
  timestamp: Date;
  isTyping?: boolean;
  unread?: boolean;
  online?: boolean;
}

export interface UserPreferences {
  brands: string[];
  budget: { min: number; max: number };
  usage: string[];
  prioritize: 'performance' | 'price' | 'camera' | 'battery';
}

export interface ConversationContext {
  sessionId: string;
  userId: string;
  startedAt: Date;
  preferences: UserPreferences;
  messages: Message[];
  recommendedProducts: string[];
  isAwaitingClarification: boolean;
  lastQueryType: string;
}

export interface AILogEntry {
  id: string;
  timestamp: Date;
  sessionId: string;
  userMessage: string;
  detectedIntent: string;
  extractedParams: {
    brand?: string;
    minRam?: number;
    maxPrice?: number;
    condition?: string;
  };
  promptUsed: string;
  modelUsed: string;
  tokensUsed: {
    input: number;
    output: number;
  };
  latencyMs: number;
  aiResponse: string;
  productsRecommended: string[];
  wasFiltered: boolean;
  filterReason?: string;
  userFeedback?: 'positive' | 'negative' | null;
  followUpAsked: boolean;
}

export interface Smartphone {
  sku: string;
  model: string;
  brand: string;
  processor: string;
  ram: number;
  storage: number;
  screenSize: number;
  price?: number;
  stock?: number;
  storeName?: string;
  condition?: string;
}

export type Theme = 'light' | 'dark';

export type QueryIntent =
  | 'brand_search'
  | 'price_filter'
  | 'spec_query'
  | 'gaming_search'
  | 'comparison'
  | 'general_help'
  | 'off_topic';
