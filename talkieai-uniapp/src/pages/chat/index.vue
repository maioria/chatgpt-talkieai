<template>
  <view class="chat-box">
    <CommonHeader background-color="#fff" :leftIcon='true' :back-fn="handleBackPage" title="聊天">
      <template v-slot:content>
        <view>{{ session.name }}</view>
      </template>
    </CommonHeader>

    <!-- 聊天内容 -->
    <view class="chat-container">
      <template v-for="(message, index) in messages" :key="message.id">
        <view class="message-content-item">
          <message-content :auto-hint="messages.auto_text_shadow" :auto-play="accountSetting.auto_playing_voice"
            :auto-pronunciation="accountSetting.auto_pronunciation" :message="message"
            ref="messageListRef"></message-content>
        </view>
      </template>
    </view>

    <!-- 底部操作栏 -->
    <view class="chat-bottom-container">
      <!-- 键盘输入 -->
      <view v-if="!inputTypeVoice" class="input-bottom-container" :style="'bottom:' + inputBottom + 'px;'">
        <view @tap="handleSwitchInputType" class="voice-icon-box">
          <image class="voice-icon" src="/static/icon_voice_fixed.png"></image>
        </view>
        <view class="input-box">
          <input class="textarea" @focus="inputFocus" confirm-type="send" @confirm="handleSendText"
            style="padding-left: 30rpx" v-model="inputText" @input="handleInput" placeholder="在这里输入文字" />
        </view>
        <view @tap="handleSendText" class="send-icon-box" :class="{ active: inputHasText }">
          <image class="send-icon" src="/static/icon_send.png"> </image>
        </view>
      </view>

      <view v-if="inputTypeVoice">
        <!-- 提示 -->
        <prompt :sessionId="session.id" v-if="menuSwitchDown"></prompt>

        <!-- 语音输入 -->
        <view class="speech-box">
          <Speech :session-id="session.id">
            <template v-slot:leftMenu>
              <image @tap="handleSwitchInputType" class="keybord-icon" src="/static/icon_keybord.png"></image>
            </template>
            <template v-slot:rightMenu>
              <image @tap="handleSwitchMenu" class="input-type-switch-btn" src="/static/icon_settings.png"></image>
            </template>
          </Speech>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import CommonHeader from "@/components/CommonHeader.vue";
import MessageContent from "./components/MessageContent.vue";
import Prompt from "./components/Prompt.vue";
import Speech from "./components/MessageSpeech.vue";
import { ref, computed, nextTick, onMounted, onBeforeUnmount, getCurrentInstance } from "vue";
import { onLoad, onShow } from "@dcloudio/uni-app";
import chatRequest from "@/api/chat";
import accountRequest from "@/api/account";
import topicRequest from "@/api/topic";
import type { Message, MessagePage, Session, AccountSettings } from "@/models/models";

const session = ref<Session>({
  id: undefined,
  type: undefined,
  messages: { total: 0, list: [] } as MessagePage,
});
const messages = ref<Message[]>([]);
const inputTypeVoice = ref(true);
const inputText = ref("");
const menuSwitchDown = ref(true);
const inputBottom = ref(0)

const messageListRef = ref([]);
const accountSetting = ref<AccountSettings>({
  auto_playing_voice: 0,
  auto_text_shadow: 0,
  auto_pronunciation: 0,
  playing_voice_speed: '1.0',
  speech_role_name_label: '',
  speech_role_name: '',
  target_language: '',
})

const $bus: any = getCurrentInstance()?.appContext.config.globalProperties.$bus;

const inputFocus = (e: any) => {
  inputBottom.value = e.detail.height;
}

// 是否已经输入文本
const inputHasText = computed(() => {
  return !!(inputText.value && inputText.value.trim());
});

const sendMessageHandler = (info: any) => {
  if (!info.text) {
    sendSpeech(info.fileName);
  } else {
    sendMessage(info.text, info.fileName);
  }
}

onLoad((option: any) => {
  initData(option.sessionId);
  uni.setNavigationBarTitle({
    title: 'TalkieAI'
  });
  console.log('Onload')
  $bus.on("SendMessage", sendMessageHandler);
});

onMounted(() => {
});

onBeforeUnmount(() => {
  $bus.off("SendMessage", sendMessageHandler);
});

onShow(() => {
  // 获取用户配置
  accountRequest.getSettings().then((data) => {
    accountSetting.value = data.data;
  });
});

/**
 * 如果用户输入回车，则发送消息
 */
const handleInput = (event: any) => {
  console.log(event);
  if (event.keyCode === 13) {
    handleSendText();
  }
}

/**
 * 发送文本
 */
const handleSendText = () => {
  if (!inputHasText.value) {
    return;
  }
  const inputTextValue = inputText.value;
  inputText.value = "";
  sendMessage(inputTextValue);
};

/**
 * 对提示、翻译的功能进行隐藏\显示的切换
 */
const handleSwitchMenu = () => {
  uni.navigateTo({
    url: `/pages/chat/settings?sessionId=${session.value.id}`,
  });
  // menuSwitchDown.value = !menuSwitchDown.value;
};

/**
 * 发送语音消息
 */
const sendSpeech = (fileName: string) => {
  const ownertTimestamp = new Date().getTime();
  const ownMessage: any = {
    id: ownertTimestamp,
    content: null,
    owner: true,
    file_name: fileName,
    role: "USER",
    auto_hint: false,
    auto_play: false,
  };
  messages.value.push(ownMessage);

  scrollToBottom();

  chatRequest.transformText({ file_name: fileName, sessionId: session.value.id })
    .then(data => {
      messages.value = messages.value.filter(
        (item) => (item.id as any) !== ownertTimestamp
      );
      let text = data.data;
      console.log(text);
      sendMessage(text, fileName)
    });
}

/**
 * 发送文字消息
 * @param message 消息内容
 * @param fileName 如果是语音发送, 则传入文件名
 */
const sendMessage = (message?: string, fileName?: string) => {
  console.log('send file name');
  const ownertTimestamp = new Date().getTime();
  const ownMessage: any = {
    id: ownertTimestamp,
    session_id: session.value.id,
    content: message,
    owner: true,
    file_name: fileName,
    role: "USER",
    auto_hint: false,
    auto_play: false,
    auto_pronunciation: false,
  };
  messages.value.push(ownMessage);
  // 防止跟前面的timestamp一样
  const timestamp = new Date().getTime() + 1;
  const aiMessage: any = {
    id: timestamp,
    session_id: session.value.id,
    content: null,
    owner: false,
    file_name: null,
    role: "ASSISTANT",
    auto_hint: false,
    auto_play: false,
    auto_pronunciation: false,
  };
  messages.value.push(aiMessage);
  scrollToBottom();
  chatRequest
    .sessionChatInvoke({
      sessionId: session.value.id,
      message: message,
      file_name: fileName,
    })
    .then((data) => {
      data = data.data;
      messages.value = messages.value.filter(
        (item) => (item.id as any) !== timestamp && (item.id as any) !== ownertTimestamp
      );

      ownMessage.id = data.send_message_id;
      ownMessage.auto_pronunciation = true;
      messages.value.push({
        ...ownMessage,
      });

      messages.value.push({
        ...aiMessage,
        id: data.id,
        content: data.data,
        auto_hint: accountSetting.value.auto_text_shadow == 1,
        auto_play: accountSetting.value.auto_playing_voice == 1,
      });

      // AI消息自动播放与模糊
      nextTick(() => {
        scrollToBottom();
      });
    })
    .catch((e) => {
      // 为用户提示错误show toast
      uni.showToast({
        title: '发送失败..',
        icon: "none",
      });
      console.error(e);
      messages.value.pop();
      messages.value.pop();
    });
};

// 切换输入方式
const handleSwitchInputType = () => {
  inputTypeVoice.value = !inputTypeVoice.value;
};

/**
 * 初始化聊天数据
 * @param sessionId
 */
const initData = (sessionId: string) => {
  chatRequest.sessionDetailsGet({ sessionId }).then((res: any) => {
    session.value = res.data;
    // 如果没有任何历史消息，则请求后台生成第一条消息
    if (session.value.messages.total === 0) {
      const timestamp = new Date().getTime();
      const aiMessage: any = {
        id: timestamp,
        session_id: session.value.id,
        content: null,
        owner: false,
        file_name: null,
        role: "ASSISTANT",
        auto_hint: false,
        auto_play: false,
        auto_pronunciation: false,
      };
      messages.value.push(aiMessage);
      chatRequest.sessionInitGreeting(sessionId).then((res: any) => {
        messages.value.pop();
        session.value.messages.list.push(res.data)
        messages.value.push({
          id: res.data.id,
          session_id: res.data.session_id,
          content: res.data.content,
          role: res.data.role,
          owner: res.data.role === "USER",
          auto_hint: accountSetting.value.auto_text_shadow == 1,
          auto_play: accountSetting.value.auto_playing_voice == 1,
          auto_pronunciation: false,
          pronunciation: null
        });
        // AI消息自动播放与模糊
        nextTick(() => {
          scrollToBottom();
        });
      })
      return;
    }

    session.value.messages.list.forEach((item) => {
      messages.value.push({
        id: item.id,
        session_id: item.session_id,
        content: item.content,
        role: item.role,
        owner: item.role === "USER",
        file_name: item.file_name,
        auto_hint: false,
        auto_play: false,
        auto_pronunciation: false,
        pronunciation: item.pronunciation
      });
    });
    scrollToBottom();
  });
};

/**
 * 回到主页面
 */
const handleBackPage = () => {
  // 如果是话题的话，提示用户是否结束些次话题
  if (session.value.type === 'TOPIC') {
    uni.showModal({
      title: '是否结束话题',
      content: '是否结束并且评分话题',
      success: (res) => {
        if (res.confirm) {
          completeTopic();
        } else if (res.cancel) {
          uni.navigateBack();
        }
      },
    });
  } else {
    uni.navigateBack();
  }
};

const completeTopic = () => {
  topicRequest.completeTopic({ session_id: session.value.id })
    .then((res) => {
      uni.navigateTo({
        url: `/pages/topic/completion?sessionId=${session.value.id}&redirectType=index`
      });
    });
}

/**
 * 滚动到最底部
 */
const scrollToBottom = () => {
  // 获取scroll-view实例
  if (messages.value.length === 0) {
    return;
  }
  // h5页面直接最原始的API
  nextTick(() => {
    uni.pageScrollTo({
      scrollTop: 10000,
      duration: 100,
    });
  });
};
</script>

<style lang="less" scoped>
.chat-box {
  display: flex;
  flex-direction: column;
  flex: 1;
}

.chat-container {
  width: 90%;
  height: 100%;
  max-width: 900px;
  margin: 0 auto;
  box-sizing: border-box;
  padding-bottom: 400rpx;

  .message-content-item {
    margin-top: 40rpx;
  }
}

.chat-bottom-container {
  background-color: #fff;
  box-sizing: border-box;
  width: 100%;
  position: fixed;
  margin: 0 auto;
  bottom: 0;
  padding-bottom: calc(env(safe-area-inset-bottom) / 2);

  .input-bottom-container {
    width: 100%;
    height: 155rpx;
    box-sizing: border-box;
    padding: 50rpx 24rpx;
    display: flex;
    gap: 28rpx;
    align-items: center;
    box-shadow: 0rpx -2rpx 4rpx 0rpx #C4C4C4;

    .voice-icon-box {
      .voice-icon {
        width: 36rpx;
        height: 48rpx;
      }
    }

    .send-icon-box {
      width: 80rpx;
      height: 80rpx;
      background-color: #d3d3d3;
      border-radius: 40rpx;
      display: flex;
      align-items: center;
      justify-content: center;

      &.active {
        background-color: #6236ff;
      }

      .send-icon {
        width: 32rpx;
        height: 32rpx;
      }
    }

    .input-box {
      flex: 1;
      height: 80rpx;

      .textarea {
        background-color: rgba(241, 241, 243, 1);
        box-sizing: border-box;
        border-radius: 40px;
        height: 100%;
      }
    }
  }

  .speech-box {
    padding-top: 32rpx;
  }

  .recorder-box {

    .keybord-icon,
    .input-type-switch-btn {
      width: 96rpx;
      height: 96rpx;

      &.up {
        transform: rotate(180deg);
      }
    }
  }
}
</style>
