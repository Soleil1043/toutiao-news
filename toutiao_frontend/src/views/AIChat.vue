<template>
  <div class="ai-chat-container">
    <van-nav-bar title="AI问答" fixed />
    
    <div class="chat-content">
      <div class="messages-container" ref="messagesContainer">
        <!-- 初始欢迎语，不参与对话历史 -->
        <div class="message ai-message">
          <div class="message-content" v-html="formatMessage(welcomeText)"></div>
        </div>

        <div 
          v-for="(message, index) in messages" 
          :key="index" 
          :class="['message', message.role === 'user' ? 'user-message' : 'ai-message']"
        >
          <div class="message-content">
            <div v-if="message.role === 'assistant' && message.content === ''" class="typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </div>
            <div v-else v-html="formatMessage(message.content)"></div>
          </div>
        </div>
      </div>
      
      <div class="input-container">
        <van-field
          v-model="userInput"
          rows="1"
          autosize
          type="textarea"
          placeholder="请输入问题..."
          class="chat-input"
          @keypress.enter.prevent="sendMessage"
        />
        <van-button 
          type="primary" 
          class="send-button" 
          :disabled="isLoading || !userInput.trim()" 
          @click="sendMessage"
        >
          发送
        </van-button>
      </div>
    </div>
    
    <tab-bar />
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, watch } from 'vue';
import TabBar from '../components/TabBar.vue';
import { showToast } from 'vant';
import * as marked from 'marked';
import DOMPurify from 'dompurify';
import { apiConfig } from '../config/api';
import { useUserStore } from '../store/user';

const userStore = useUserStore();

// 初始欢迎语，仅做展示，不参与对话历史
const welcomeText = '你好！我是AI助手，有什么可以帮助你的吗？';

// 聊天消息：只保存真实的用户输入和 AI 回复（不含初始欢迎语）
const messages = ref([]);
const userInput = ref('');
const messagesContainer = ref(null);
const isLoading = ref(false);

// 从 api.js 读取后端地址
const baseURL = apiConfig.baseURL;
const chatApiUrl = `${baseURL}/api/chat/stream`;

// 格式化消息内容（支持Markdown）
const formatMessage = (content) => {
  if (!content) return '';
  return DOMPurify.sanitize(marked.parse(content));
};

// 发送消息
const sendMessage = async () => {
  if (!userInput.value.trim() || isLoading.value) return;
  // 统一登录判断逻辑
  if (!userStore.getLoginStatus) {
    showToast('请先登录');
    return;
  }
  // 添加用户消息
  const userMessage = userInput.value.trim();
  messages.value.push({ role: 'user', content: userMessage });
  userInput.value = '';

  // 添加AI占位消息
  messages.value.push({ role: 'assistant', content: '' });

  await nextTick();
  scrollToBottom();

  isLoading.value = true;
  try {
    await fetchAIResponse();
  } catch (error) {
    console.error('AI 聊天请求失败:', error);
    messages.value[messages.value.length - 1].content = `请求失败：${error.message || '网络异常'}`;
  } finally {
    isLoading.value = false;
    await nextTick();
    scrollToBottom();
  }
};

// 请求后端接口
const fetchAIResponse = async () => {
  // 取真实历史消息（去掉当前正在等待的 AI 占位消息）
  const historyMessages = messages.value
    .slice(0, -1)
    .map(msg => ({ role: msg.role, content: msg.content }));

  const response = await fetch(chatApiUrl, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${userStore.token}`,
    },
    // system prompt 由后端统一注入（config/ai_conf.py 的 AI_SYSTEM_PROMPT），
    // 前端只传真实对话历史，防止被篡改、集中管理
    body: JSON.stringify({ messages: historyMessages })
  });

  if (!response.ok) {
    if (response.status === 401) {
      showToast('登录已过期，请重新登录');
    }
    throw new Error('接口请求异常');
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let aiResponse = '';
  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    // 流式数据可能跨 chunk 截断，先拼进 buffer 再按行切分，最后一行可能不完整留到下一轮
    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n');
    buffer = lines.pop() || '';

    let isDone = false;
    for (const line of lines) {
      const trimmed = line.trim();
      if (!trimmed.startsWith('data: ')) continue;
      const data = trimmed.slice(6);

      if (data === '[DONE]') {
        isDone = true;
        break;
      }
      if (!data.startsWith('{')) continue;
      try {
        // OpenAI 兼容流式格式：内容在 choices[0].delta.content
        const json = JSON.parse(data);
        const delta = json.choices?.[0]?.delta?.content ?? json.content ?? '';
        aiResponse += delta;
        messages.value[messages.value.length - 1].content = aiResponse;
        await nextTick();
        scrollToBottom();
      } catch (e) {
        console.warn('SSE 数据解析失败:', e);
      }
    }
    if (isDone) break;
  }
};

// 滚动到底部
const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
  }
};

// 监听消息自动滚动
watch(messages, () => {
  nextTick(scrollToBottom);
}, { deep: true });

onMounted(() => {
  scrollToBottom();
});
</script>

<style scoped>
.ai-chat-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  padding-top: 46px;
  padding-bottom: 50px;
  box-sizing: border-box;
}

.chat-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
}

.message {
  margin-bottom: 10px;
  max-width: 80%;
}

.user-message {
  margin-left: auto;
}

.ai-message {
  margin-right: auto;
}

.message-content {
  padding: 10px;
  border-radius: 10px;
  word-break: break-word;
}

.user-message .message-content {
  background-color: #007aff;
  color: white;
}

.ai-message .message-content {
  background-color: #f2f2f2;
  color: #333;
}

.input-container {
  display: flex;
  padding: 10px;
  border-top: 1px solid #eee;
  background-color: #fff;
}

.chat-input {
  flex: 1;
  margin-right: 10px;
}

.send-button {
  align-self: flex-end;
}

.message-content pre {
  background-color: #f8f8f8;
  padding: 10px;
  border-radius: 5px;
  overflow-x: auto;
}

.message-content code {
  background-color: rgba(0, 0, 0, 0.05);
  padding: 2px 4px;
  border-radius: 3px;
}

.typing-indicator {
  display: flex;
  padding: 5px;
}

.typing-indicator span {
  height: 8px;
  width: 8px;
  background-color: #999;
  border-radius: 50%;
  margin: 0 2px;
  animation: bounce 1.5s infinite ease-in-out;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes bounce {
  0%, 60%, 100% { transform: translateY(0); }
  30% { transform: translateY(-5px); }
}

:deep(pre) {
  background-color: #f0f0f0;
  padding: 10px;
  border-radius: 4px;
  overflow-x: auto;
}

:deep(code) {
  font-family: monospace;
  background-color: #f0f0f0;
  padding: 2px 4px;
  border-radius: 4px;
}

:deep(p) { margin: 8px 0; }
:deep(ul), :deep(ol) { padding-left: 20px; }
:deep(a) { color: #1989fa; text-decoration: none; }
</style>