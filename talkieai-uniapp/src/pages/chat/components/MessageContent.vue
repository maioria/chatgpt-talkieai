<template>
  <view class="message-container" :class="containerClass">
    <!-- loading -->
    <view v-if="!message.content" class="loading-box">
      <Loading />
    </view>
    <!-- 具体内容 -->
    <view v-else class="message-box">
      <view class="message-text-box" :class="{ 'own-text-box': message.owner }">
        <!-- AI消息 -->
        <view v-if="!message.owner" class="assistant-text-box">
          <FunctionalText ref="functionalTextRef" :auto-play="message.auto_play || false" :messageId="message.id"
            :wordClickable="true" :text="message.content" :translateShow="translateShow" :textShadow="textShadow" />
          <view class="divider"></view>
          <view class="action-container">
            <view class="btn-box" :class="{ active: translateShow }">
              <image class="action-icon" @tap="handleTranslateText" src="/static/icon_translate.png" />
            </view>
            <view class="btn-box collect-btn-box">
              <Collect type="MESSAGE" :messageId="message.id || ''" />
            </view>
            <view class="btn-box">
              <image class="action-icon" @tap="handleCopyText" src="/static/icon_copy_text.png" />
            </view>
            <view class="btn-box" :class="{ active: textShadow }">
              <image class="action-icon" @tap="handleHint" src="/static/icon_hint.png" />
            </view>
          </view>
        </view>

        <!-- 用户消息 -->
        <view v-else class="account-text-container">
          <view class="account-text-box">

            <!-- 展示语音分析结果 -->
            <!-- <TextPronunciation v-if="message.pronunciation" :content="message.content" :pronunciation="message.pronunciation" @wordClick="handleWordDetail" />
            
            <view v-else>{{ message.content }}</view> -->
            <view>{{ message.content }}</view>

            <!-- 语音播放 -->
            <view v-if="message.file_name" class="speech-box">
              <AudioPlayer direction="right" :fileName="message.file_name" />
            </view>
          </view>
        </view>
      </view>

      <!-- 语法 -->
      <view v-if="message.owner" class="grammar-outter-box">
        <LoadingRound v-if="grammarLoading" class="grammar-box" />
        <view v-else-if="message.pronunciation" class="grammar-box"  @tap="handleGrammar">
          <image class="grammar-icon" src="/static/icon_grammar.png" />
          <text class="grammar-score">{{ utils.removeDecimal(message.pronunciation.pronunciation_score) }}</text>
        </view>
        <view v-else class="grammar-box"  @tap="handleGrammar">
          <image class="grammar-icon" src="/static/icon_grammar.png" />
          <text>语法</text>
        </view>
      </view>
    </view>
    <MessageGrammar ref="messageGrammarRef" />
  </view>
</template>
<script setup lang="ts">
import { ref, computed, nextTick, onMounted } from "vue";
import FunctionalText from "@/components/FunctionalText.vue";
import AudioPlayer from "@/components/AudioPlayer.vue";
import MessageGrammar from "./MessageGrammarPopup.vue";
import TextPronunciation from "./TextPronunciation.vue";
import Collect from "@/components/Collect.vue";
import type { Message, MessagePage, Session } from "@/models/models";
import Loading from "@/components/Loading.vue";
import LoadingRound from "@/components/LoadingRound.vue";
import chatRequest from "@/api/chat";
import utils from "@/utils/utils";

const functionalTextRef = ref(null);
const messageGrammarRef = ref(null);
const grammarLoading = ref(false);
const translateShow = ref(false);
const textShadow = ref(false);

const props = defineProps<{
  message: Message;
}>();

onMounted(() => {
  if (props.message.auto_hint && props.message.auto_hint === true) {
    textShadow.value = true;
  }
  if (props.message.auto_pronunciation) {
    autoPronunciation();
  }
});

const ownerMessage = computed(() => {
  return props.message.owner;
});
const containerClass = computed(() => {
  const messagePosition = props.message.owner ? "right" : "left";
  return `${messagePosition}-content`;
});

const handleTranslateText = () => {
  translateShow.value = !translateShow.value;
};

const handleCopyText = () => {
  uni.setClipboardData({
    data: props.message.content,
    success: () => {
      uni.showToast({
        title: "复制成功",
        icon: "none",
      });
    },
  });
};

const handleHint = () => {
  textShadow.value = !textShadow.value;
};

const handleGrammar = (type:string|undefined) => {
  messageGrammarRef.value.open(
    props.message.id,
    props.message.content,
    props.message.file_name,
    props.message.session_id,
    type
  );
};

const handleWordDetail = (word: string) => {
  handleGrammar('pronunciation')
};

/**
 * 用于显露到外面的方法，用于外部调用播放
 */
const autoPlayAudio = () => {
  nextTick(() => {
    functionalTextRef.value.autoPlayAudio();
  });
};

const autoPronunciation = () => {
  grammarLoading.value = true;
  chatRequest
    .pronunciationInvoke({ message_id: props.message.id })
    .then((data) => {
      // 更新message对象的pronunciation属性
      props.message.pronunciation = data.data;
      grammarLoading.value = false;
    });
};

/**
 * 用于显露到外面的方法，用于外部调用模糊
 */
const autoHandleHint = () => {
  handleHint();
};

defineExpose({
  autoPlayAudio,
  autoHandleHint,
  autoPronunciation,
});
</script>
<style lang="less" scoped>
.speech-box {
  display: flex;
  align-items: center;
  height: 22px;
}

.message-container {
  display: flex;
  flex-direction: column;

  .message-box {
    max-width: 80%;

    .message-text-box {
      padding: 28rpx 36rpx;
      border-radius: 8rpx 30rpx 30rpx;
      color: #333;
      display: flex;
      flex-direction: column;

      &.own-text-box {
        border-radius: 30rpx 8rpx 30rpx 30rpx;
      }

      .text-shadow {
        filter: blur(5px);
      }
    }
  }

  .divider {
    margin: 14px 0 8px;
    width: 100%;
    height: 1px;
    background: rgba(0, 0, 0, 0.08);
  }

  &.right-content {
    align-items: flex-end;

    .message-text-box {
      background-color: #ede8ff;
    }

    .account-text-container {
      .account-text-box {
        display: flex;
        flex-direction: row-reverse;
        gap: 16rpx;
      }
    }

    .grammar-outter-box {
      display: flex;
      flex-direction: row-reverse;

      .grammar-box {
        margin-top: 12rpx;
        display: flex;
        border: #979797 1rpx solid;
        padding: 12rpx 28rpx;
        align-items: center;
        border-radius: 10rpx;

        .grammar-icon {
          width: 28rpx;
          height: 28rpx;
          margin-right: 14rpx;
        }

        .grammar-score {
          color: rgb(17, 165, 129);
        }
      }
    }
  }

  &.left-content {
    align-items: flex-start;

    .message-text-box {
      background-color: #f1f1f3;
    }

    .action-container {
      display: flex;

      // gap: 28rpx;
      .btn-box {
        margin-left: 16rpx;
        height: 48rpx;
        width: 48rpx;
        display: flex;
        justify-content: center;
        align-items: center;
        // padding: 8rpx;

        // &.collect-btn-box {
        //   width: 32rpx;
        //   height: 30rpx;
        // }

        &.active {
          background-color: #fff;
        }

        &:first-child {
          margin-left: 0;
        }
      }
    }

    .action-icon {
      width: 32rpx;
      height: 32rpx;
    }
  }
}
</style>
