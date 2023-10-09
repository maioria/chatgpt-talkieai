<template>
  <view @tap="handleSpeech" class="speech-container" :title="speechLoading">
    <view class="playing-ico">
      <LoadingRound v-if="transformFileLoading"></LoadingRound>
      <template v-else>
        <image
            v-if="speechLoading"
            class="icon message-playing-icon play-ico"
            :class="{ reverse: direction && direction == 'right' }"
            src="/static/voice_playing.gif"
            mode="heightFix"
        ></image>
        <image
            v-else
            class="icon message-playing-icon playing-ico"
            :class="{ reverse: direction && direction == 'right' }"
            src="/static/voice_play.png"
            mode="heightFix"
        ></image>
      </template>
    </view>
  </view>
</template>
<script setup lang="ts">
/**
 * @description: 语音播放组件
 */
import { ref, onMounted, inject } from "vue";
// import audioPlayer from "./audioPlayerExecuter";
import chatRequest from "@/api/chat";
import LoadingRound from "@/components/LoadingRound.vue";
import { nextTick } from "vue";

import audioPlayer from "./audioPlayerExecuter"; // 导入共享对象
import __config from "@/config/env";

const props = defineProps<{
  messageId?: string | null;
  fileName?: string | null;
  content?: string | null;
  sessionId?: string | null;
  direction?: "right" | "left";
  speech_role_name?: string | null;
  autoPlay?: Boolean;
}>();

const transformFileLoading = ref(false);
const speechLoading = ref(false);
const speechUrl = ref("");

onMounted(() => {
  if (props.autoPlay) {
    handleSpeech();
  }
});

const handleSpeech = async () => {
  // 语音文件直接播放
  if (props.fileName) {
    audioPlayer.playAudio({
      audioUrl: `${__config.basePath}/files/${props.fileName}`,
      listener: {
        playing: () => {
          speechLoading.value = true;
        },
        success: () => {
          speechLoading.value = false;
        },
        error: () => {
          speechLoading.value = false;
        },
      },
    });
    return;
  }

  // 聊天消息直接转换成语音
  if (props.messageId) {
    transformFileLoading.value = true;
    audioPlayer.playAudio({
      audioUrl: `${__config.basePath}/speech?message_id=${props.messageId}&x_token_query=${uni.getStorageSync("x-token") ? uni.getStorageSync("x-token") : ""}`,
      listener: {
        playing: () => {
          transformFileLoading.value = false;
          speechLoading.value = true;
        },
        success: () => {
          transformFileLoading.value = false;
          speechLoading.value = false;
        },
        error: () => {
          transformFileLoading.value = false;
          speechLoading.value = false;
        },
      },
    });
    return;
  }

  // 内容直接转换成语音
  if (props.content) {
    try {
      transformFileLoading.value = true;
      // const data = await chatRequest.speechContent({
      //   content: props.content,
      //   speech_role_name: props.speech_role_name,
      //   session_id: props.sessionId,
      // });
      // transformFileLoading.value = false;
      // speechLoading.value = true;
      // const audioUrl = data.data.file;
      let audioUrl = `${__config.basePath}/speech-content?content=${props.content}`;
      if (props.speech_role_name) {
        audioUrl += `&speech_role_name=${props.speech_role_name}`;
      }
      if (props.sessionId) {
        audioUrl += `&session_id=${props.sessionId}`;
      }
      if (uni.getStorageSync("x-token")) {
        audioUrl += `&x_token_query=${uni.getStorageSync("x-token")}`;
      }
      audioPlayer.playAudio({
        audioUrl: audioUrl,
        listener: {
          playing: () => {
            transformFileLoading.value = false;
            speechLoading.value = true;
          },
          success: () => {
            speechLoading.value = false;
          },
          error: () => {
            speechLoading.value = false;
          },
        },
      });
    } catch (error) {
      speechLoading.value = false;
    }
    return;
  }
};

/**
 * 用于显露到外面的方法，用于外部调用播放
 */
const autoPlayAudio = () => {
  nextTick(() => {
    handleSpeech();
  });
};

defineExpose({
  autoPlayAudio,
});
</script>

<style lang="less" scoped>
.speech-container {
  width: 22rpx;
  height: 28rpx;
  display: flex;
  align-items: center;
  .playing-ico {
    width: 22rpx;
    height: 28rpx;
    display: flex;
    align-items: center;
    .icon {
      width: 22rpx;
      height: 28rpx;

      &.reverse {
        transform: rotateY(180deg);
      }
    }
  }
}
</style>
