/**
 * ============================================
 * AI 行业脉搏 - 开发者配置文件
 * ============================================
 * 
 * 【重要】此文件包含敏感信息，请按以下步骤操作：
 * 
 * 1. 首次使用：将此文件复制为 config.js
 *    cp config.example.js config.js
 * 
 * 2. 在 config.js 中填入您的 API Key
 * 
 * 3. 在 .gitignore 中添加以下行，避免提交到 GitHub：
 *    config.js
 * 
 * 4. 如果使用 CI/CD，可以在环境变量中配置，格式如下：
 *    window.AI_PULSE_CONFIG = {
 *        apiKey: process.env.API_KEY,
 *        apiBaseUrl: 'https://api.openai.com/v1',
 *        model: 'gpt-4o'
 *    };
 */

window.AI_PULSE_CONFIG = {
    // ============================================
    // API 配置（请填入您的 API Key）
    // ============================================
    apiKey: 'YOUR_API_KEY_HERE',
    
    // ============================================
    // API 地址配置
    // 支持：OpenAI、DeepSeek、硅基流动 等兼容 OpenAI 格式的 API
    // ============================================
    apiBaseUrl: 'https://api.openai.com/v1',
    
    // ============================================
    // 模型配置
    // 常用模型：gpt-4o、gpt-4-turbo、gpt-3.5-turbo、deepseek-chat 等
    // ============================================
    model: 'gpt-4o'
};
