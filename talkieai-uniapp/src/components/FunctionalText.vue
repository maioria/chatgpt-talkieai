<template>
  <view class="functional-text-container" @tap="handleSpaceClick">
    <view class="text-box">
      <!-- 点击后可再次点击查看单词详情 -->
      <view
        v-if="wordClickable"
        v-show="!clickAbleWord"
        @tap.stop="handleWordClick"
        class="text-content"
        :class="{ 'text-shadow': textShadow }"
      >
        <text>
          {{ text }}
        </text>
      </view>
      <view v-else class="text-content">
        <text>{{ text }}</text>
      </view>

      <view v-if="wordClickable && clickAbleWord && text">
        <view
          v-for="(word, index) in text.split(' ')"
          :key="index"
          @tap.stop="handleAnalysis(word)"
          class="clickable-word"
        >
          <text class="word-text">
            {{ word }}
          </text>
        </view>
      </view>
      <!-- 语音播放 -->
      <AudioPlayer
        class="audio-player-container"
        ref="audioPlayRef"
        :autoPlay="autoPlay"
        :sessionId="sessionId"
        :messageId="messageId"
        :content="text"
      />
    </view>
    <!-- 文本翻译 -->
    <view v-if="translateShow || translateLoading" class="translate-box">
      <view v-show="!translateLoading" class="translate-content">
        <text>{{ translateText }}</text>
      </view>
      <view class="translate-loading" v-show="translateLoading">
        <LoadingRound />
      </view>
    </view>

    <!-- 单词详情弹出框 -->
    <WordAnalysisPopup ref="wordAnalysisPopup" />
  </view>
</template>
<script setup lang="ts">
import { ref, watch, onMounted, toRefs, nextTick } from "vue";
import AudioPlayer from "./AudioPlayer.vue";
import WordAnalysisPopup from "./WordAnalysisPopup.vue";
import { defineProps } from "vue";
import chatRequest from "@/api/chat";
import LoadingRound from "@/components/LoadingRound.vue";

// 增加translateShow boolean类型，默认为false
const props = defineProps<{
  text?: string | null;
  textShadow?: Boolean;
  sessionId?: string | null;
  messageId?: string | null;
  wordClickable?: Boolean;
  translateShow?: Boolean;
  autoPlay?: Boolean;
}>();

const translateLoading = ref(false);
const translateText = ref("");
const clickAbleWord = ref(false);
const wordAnalysisPopup = ref(null);
const audioPlayRef = ref(null);

onMounted(() => {});

watch(
  () => props.translateShow,
  (newVal, oldVal) => {
    if (newVal && !translateText.value) {
      initTranslateData();
    }
  },
  { deep: true }
);
const initTranslateData = () => {
  if (translateText.value) {
    return;
  }
  translateLoading.value = true;
  if (props.messageId) {
    chatRequest
      .translateInvoke({
        message_id: props.messageId,
      })
      .then((data) => {
        translateText.value = data.data;
      })
      .catch((e) => {
        translateText.value = "翻译出错";
      })
      .finally(() => {
        translateLoading.value = false;
      });
  } else {
    chatRequest
      .translateText({
        text: props.text,
      })
      .then((data) => {
        translateText.value = data.data;
      })
      .catch((e) => {
        translateText.value = "翻译出错";
      })
      .finally(() => {
        translateLoading.value = false;
      });
  }
};

const handleSpaceClick = () => {
  clickAbleWord.value = false;
};

const handleWordClick = () => {
  if (props.textShadow) {
    // 模糊情况下不能点击查看单词详情
    return;
  }
  clickAbleWord.value = true;
};

const handleAnalysis = (word: string) => {
  // ref.wordAnalysisPopup.open(word);
  // 需要先去掉单词首尾的符号
  const reg = /[^a-zA-Z]/g;
  word = word.replace(reg, "");
  nextTick(() => {
    setTimeout(() => {
      wordAnalysisPopup.value.open(word);
    }, 100);
  });
};

const autoPlayAudio = () => {
  nextTick(() => {
    audioPlayRef.value.autoPlayAudio();
  });
};

defineExpose({
  initTranslateData,
  autoPlayAudio,
});
</script>
<style lang="less" scoped>
.functional-text-container {
  width: 100%;
  color: #333;
  display: flex;
  flex-direction: column;

  .text-box {
    display: flex;
    justify-content: space-between;

    .text-shadow {
      filter: blur(5px);
    }

    .text-content {
      flex: 1;
    }

    .clickable-word {
      display: inline-block;
      cursor: pointer;
      border-radius: 4px;
      margin-right: 4px;
      word-break: break-word;
      word-wrap: break-word;
      box-sizing: border-box;
      white-space: pre-wrap;
      text-align: center;

      .word-text {
        background-color: #d5d9e0;
      }

      &:hover .word-text {
        background-color: #c0d3db;
      }
    }

    .audio-player-container {
      margin-left: 8rpx;
      height: 22px;
      display: flex;
      align-items: center;
    }
  }

  .translate-box {
    margin-top: 32rpx;
  }
}
</style>
