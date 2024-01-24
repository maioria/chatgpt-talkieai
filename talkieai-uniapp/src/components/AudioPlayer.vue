<template>
  <view @tap="handleSpeech" class="speech-container" :title="speechLoading">
    <view class="playing-ico">
      <LoadingRound v-if="transformFileLoading"></LoadingRound>
      <template v-else>
        <image v-if="speechLoading" class="icon message-playing-icon play-ico" style="width: 36rpx;height:36rpx;"
          :class="{ reverse: direction && direction == 'right' }" src="/static/voice_playing.gif" mode="heightFix">
        </image>
        <image v-else class="icon message-playing-icon playing-ico" style="width: 36rpx;height:36rpx;"
          :class="{ reverse: direction && direction == 'right' }" src="/static/voice_play.png" mode="heightFix"></image>
      </template>
    </view>
  </view>
</template>
<script setup lang="ts">
/**
 * @description: 语音播放组件
 */
import { ref, onMounted, inject } from "vue";
import LoadingRound from "@/components/LoadingRound.vue";
import { nextTick } from "vue";
import utils from "@/utils/utils";

import audioPlayer from "./audioPlayerExecuter"; // 导入共享对象
import __config from "@/config/env";

const props = defineProps<{
  messageId?: string | null;
  fileName?: string | null;
  content?: string | null;
  direction?: "right" | "left";
  autoPlay?: Boolean;
  speechRoleName?: string | null;
  speechRoleStyle?: string | null;
  sessionId?: string | null;
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
  let audioUrl = '';
  if (props.fileName) {   // 语音文件直接播放
    audioUrl = utils.getVoiceFileUrl(props.fileName);
  } else {
    if (props.messageId) {   // 聊天信息转换成语音文件再播放
      transformFileLoading.value = true;
      audioUrl = `${__config.basePath}/message/speech?message_id=${props.messageId}`;
    } else if (props.content) {  // 内容转换成语音后播放
      transformFileLoading.value = true;
      audioUrl = `${__config.basePath}/message/speech-content?content=${props.content}`;
      if (props.speechRoleName) {
        audioUrl += `&speech_role_name=${props.speechRoleName}`;
      }
      if (props.speechRoleStyle) {
        audioUrl += `&speech_role_style=${props.speechRoleStyle}`;
      }
      if (props.sessionId) {
        audioUrl += `&session_id=${props.sessionId}`;
      }
    }
    if (uni.getStorageSync("x-token")) {
      audioUrl += `&x_token_query=${uni.getStorageSync("x-token")}`;
    }
  }
  console.log(audioUrl)
  audioPlayer.playAudio({
    audioUrl: audioUrl,
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
  display: flex;
  align-items: center;

  .playing-ico {
    display: flex;
    align-items: center;

    .icon {
      width: 32rpx;
      height: 32rpx;

      &.reverse {
        transform: rotateY(180deg);
      }
    }
  }
}
</style>
