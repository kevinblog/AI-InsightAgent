/**
 * AI 行业脉搏 - 前端配置
 * 
 * 使用说明：
 * 1. 将此文件复制为 config.js
 * 2. 填写您的 API 配置
 */

const API_CONFIG = {
    // API 基础地址（后端服务地址）
    API_BASE_URL: 'http://localhost:8000',
    
    // AI API 配置（可选，不填则使用 Mock 数据）
    AI_API_KEY: '',          // DeepSeek API Key
    AI_API_BASE_URL: 'https://api.deepseek.com/v1',
    AI_MODEL: 'deepseek-chat'
};

console.log('配置已加载:', API_CONFIG);
