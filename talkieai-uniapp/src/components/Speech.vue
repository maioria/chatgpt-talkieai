<template>
  <view class="speech-container">
    <!-- 未开始录音 -->
    <view v-if="!recorder.start && !recorder.completed" class="recorder-box">
      <slot name="leftMenu">
        <view></view>
      </slot>
      <view @tap="handleSpeech" class="recorder-btn-box">
        <view class="voice-circle">
          <image class="voice-icon" src="/static/icon_voice.png"></image>
        </view>
      </view>
      <slot name="rightMenu">
        <view></view>
      </slot>
    </view>

    <!-- 开始录音 -->
    <view v-if="recorder.start" @tap="handleSpeechEnd" class="recordering-box">
      <view class="outter-circle animated"></view>
      <view class="recordering-circle">
        <view class="recordering-square"></view>
      </view>
    </view>

    <!-- 录音结束 -->
    <view v-if="recorder.completed" class="recorder-completed-box">
      <view @tap="handleTrash" class="trash-btn-box">
        <image class="trash-btn" src="/static/icon_trash.png"></image>
      </view>
      <view @tap="handlePlaySpeech" class="play-btn-box">
        <image
          v-if="!voicePlaying"
          class="play-btn"
          src="/static/icon_menu_play.png"
        >
        </image>
        <image
          v-else="voicePlaying"
          class="play-btn"
          style="width: 100%; height: 100%"
          src="/static/menu_voice_playing.gif"
        ></image>
      </view>
      <view @tap="handleSend" class="send-btn-box">
        <LoadingRound v-if="recorder.processing"></LoadingRound>
        <image
          v-if="!recorder.processing"
          class="send-btn"
          src="/static/icon_send.png"
        ></image>
      </view>
    </view>
  </view>
</template>
<script setup lang="ts">
import { ref, defineEmits, getCurrentInstance } from "vue";
import LoadingRound from "@/components/LoadingRound.vue";
import speech from "./speechExecuter";
// import audioPlayer from "@/components/audioPlayerExecuter";
import audioPlayer from "./audioPlayerExecuter"; // 导入共享对象

const emit = defineEmits();

const $bus: any = getCurrentInstance()?.appContext.config.globalProperties.$bus;
const recorder = ref({
  start: false,
  processing: false,
  completed: false,
  voiceFileName: null,
});
const voicePlaying = ref(false);

/**
 * 开始录音
 */
const handleSpeech = () => {
  if (recorder.value.start) {
    speech.handleEndVoice();
    return;
  }

  audioPlayer.stopAudio();
  recorder.value.start = true;
  recorder.value.completed = false;
  speech.handleVoiceStart({
    processing: () => {
      recorder.value.processing = true;
    },
    success: ({ voiceFileName }) => {
      recorder.value.voiceFileName = voiceFileName;
      recorder.value.processing = false;
      recorder.value.start = false;
      recorder.value.completed = true;
    },
    interval: (interval: any) => {
      recorder.value.remainingTime = interval;
    },
    cancel: () => {
      recorder.value.processing = false;
      recorder.value.start = false;
    },
    error: (err: any) => {
      recorder.value.processing = false;
      recorder.value.start = false;
    },
  });
};

/**
 * 结束录音
 */
const handleSpeechEnd = () => {
  speech.handleEndVoice();
};

/**
 * 删除录音
 */
const handleTrash = () => {
  recorder.value.completed = false;
};

/**
 * 播放录音
 */
const handlePlaySpeech = () => {
  if (!recorder.value.voiceFileName) {
    console.error("没有语音文件");
    return;
  }
  audioPlayer.playAudio({
    audioUrl: recorder.value.voiceFileName,
    listener: {
      playing: () => {
        voicePlaying.value = true;
        console.log(voicePlaying.value);
      },
      success: () => {
        voicePlaying.value = false;
        console.log(voicePlaying.value);
      },
      error: () => {
        voicePlaying.value = false;
      },
    },
  });
};

/**
 * 发送语音
 */
const handleSend = () => {
  if (!recorder.value.voiceFileName) {
    console.error("没有语音文件");
    return;
  }
  emit("success", {
    fileName: recorder.value.voiceFileName,
  });
  recorder.value.completed = false;
};
</script>
<style lang="scss" scoped>
.speech-container {
  min-height: 125rpx;
  height: 236rpx;
}

.recorder-btn-box,
.play-btn-box {
  margin: 0 100rpx;
}

.recorder-completed-box,
.recorder-box, .recordering-box {
  padding: 0 90rpx 0 90rpx;
  display: flex;
  position: relative;
  box-sizing: border-box;
  width: 100%;
  align-items: center;
  justify-content: center;
}

.recorder-completed-box {
  .recorder-btn-box {
    width: 176rpx;
    height: 176rpx;
    background-color: rgba(236, 230, 254, 1);
    border-radius: 87px;
    padding: 20rpx;
    box-sizing: border-box;
  }

  .trash-btn-box {
    min-width: 96rpx;
    height: 96rpx;
    border-radius: 48rpx;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: #d3d3d3;

    .trash-btn {
      width: 32rpx;
      height: 32rpx;
    }
  }

  .play-btn-box {
    min-width: 136rpx;
    height: 136rpx;
    border-radius: 88rpx;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: rgba(98, 54, 255, 1);

    .play-btn {
      width: 32rpx;
      height: 48rpx;
    }
  }

  .send-btn-box {
    min-width: 96rpx;
    height: 96rpx;
    border-radius: 48rpx;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: rgba(98, 54, 255, 1);

    &.translating {
      background-color: rgba(211, 211, 211, 1);
    }

    .send-btn {
      width: 32rpx;
      height: 32rpx;
    }
  }
}

.recorder-completed-box {
  padding-top: 20rpx;
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

  .recorder-btn-box {
    width: 176rpx;
    height: 176rpx;
    background-color: rgba(236, 230, 254, 1);
    border-radius: 87px;
    padding: 20rpx;
    box-sizing: border-box;

    .voice-circle {
      width: 136rpx;
      height: 136rpx;
      background-color: rgba(98, 54, 255, 1);
      border-radius: 70px;
      padding: 44rpx 50rpx 44rpx 50rpx;
      box-sizing: border-box;

      .voice-icon {
        width: 36rpx;
        height: 48rpx;
      }
    }
  }
}

.recordering-box {

  .outter-circle.animated {
    width: 176rpx;
    height: 176rpx;
    background-color: rgba(251, 107, 107, 0.28);
    position: relative;
    border-radius: 50%;
    animation: scale-40df7b08 2s infinite;

    @keyframes scale-40df7b08 {
      0% {
        transform: scale(1);
        opacity: 1;
      }

      50% {
        transform: scale(0.8);
        opacity: 0.9;
      }

      to {
        transform: scale(1);
        opacity: 1;
      }
    }
  }

  .recordering-circle {
    position: absolute;
    background-color: rgba(251, 107, 107, 1);
    border-radius: 70px;
    padding: 44rpx 44rpx 44rpx 44rpx;
    box-sizing: border-box;

    .recordering-square {
      position: relative;
      background-color: rgba(255, 255, 255, 1);
      border-radius: 6px;
      width: 48rpx;
      height: 48rpx;
      box-sizing: border-box;
    }
  }
}
</style>
