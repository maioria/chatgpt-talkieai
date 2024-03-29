<template>
  <!-- 发音评估 -->
  <view>
    <view class="pronunciation-content">
      <loading-round v-if="pronunciationLoading" />
      <view v-if="pronunciationResult">
        <Rate :rate="utils.removeDecimal(pronunciationResult.pronunciation_score)" />
      </view>
      <view v-if="pronunciationResult" class="pronunciation-tips"> 点击查看单词评分 </view>

      <TextPronunciation v-if="pronunciationResult" :content="messageContent" :pronunciation="pronunciationResult" @wordClick="handleWordDetail" />

      <view class="voice-box">
        <view class="ai-voice-box">
          <image class="voice-avatar" :src="globalUserInfo.teacher_avatar || '/static/ai-robot.jpg'"></image>
          <audio-player :content="messageContent" :sessionId="sessionId"></audio-player>
        </view>

        <view v-if="fileName" class="original-voice-box">
          <view class="my-voice-avatar-box">
            <text class="avatar-text"> 我 </text>
          </view>
          <audio-player :fileName="practiceFileName || fileName"></audio-player>
        </view>
      </view>
    </view>
    <view class="practice-box">练习</view>
    <speech @success="handleSuccess"></speech>
  </view>
</template>
<script setup lang="ts">
import { ref, defineEmits } from "vue";
import AudioPlayer from "@/components/AudioPlayer.vue";
import LoadingRound from "@/components/LoadingRound.vue";
import Speech from "@/components/Speech.vue";
import Rate from "@/components/Rate.vue";
import TextPronunciation from "./TextPronunciation.vue";
import chatRequest from "@/api/chat";
import { useUserInfo } from "@/global/globalCount.hooks";
import utils from '@/utils/utils';
import type { Word } from '@/models/models';

const props = defineProps<{
  messageId: string;
  sessionId?: string;
  messageContent: string;
  fileName?: string;
}>();
const { globalUserInfo, globalLoading } = useUserInfo();
const emit = defineEmits();
const pronunciationLoading = ref(false);
const pronunciationResult = ref(null);
const practiceFileName = ref(null);

const initData = () => {
  if (pronunciationResult.value || !props.fileName) {
    return;
  }
  pronunciationLoading.value = true;
  chatRequest
    .pronunciationInvoke({ message_id: props.messageId })
    .then((data) => {
      pronunciationResult.value = data.data;
    }).finally(() => {
      pronunciationLoading.value = false;
      console.log(pronunciationLoading.value)
    });
};

const handleSuccess = (data: any) => {
  pronunciationLoading.value = true;
  pronunciationResult.value = null;
  chatRequest
    .messagePractice({ message_id: props.messageId, file_name: data.fileName })
    .then((resp) => {
      practiceFileName.value = data.fileName;
      pronunciationResult.value = resp.data;
    }).finally(() => {
      pronunciationLoading.value = false;
      console.log(pronunciationLoading.value)
    });
};
const handleWordDetail = (word: Word) => {
  emit("wordClick", word);
};
defineExpose({
  initData,
});
</script>
<style lang="scss" scoped>
.pronunciation-content {
  .pronunciation-tips {
    background-color: #FBF7EB;
    color: #917046;
    border-radius: 30rpx;
    margin-top: -20rpx;
    padding: 8rpx 0 8rpx 32rpx;
  }

  .voice-box {
    margin-top: 32rpx;
    display: flex;
    gap: 64rpx;
    justify-content: center;

    .ai-voice-box,
    .original-voice-box {
      display: flex;
      justify-content: center;
      align-items: center;
      box-shadow: 0px 0px 8px 0px rgba(196, 196, 196, 1);
      background-color: rgba(255, 255, 255, 1);
      border-radius: 42px;
      width: 146rpx;
      padding: 6rpx 24rpx 6rpx 4rpx;
      justify-content: space-between;
    }

    .voice-avatar {
      width: 72rpx;
      height: 72rpx;
      border-radius: 72rpx;
    }

    .my-voice-avatar-box {
      width: 72rpx;
      height: 72rpx;
      background: #6236ff;
      border-radius: 36rpx;
      display: flex;
      justify-content: center;
      align-items: center;

      .avatar-text {
        width: 38rpx;
        height: 50rpx;
        font-size: 36rpx;
        color: #fff;
      }
    }
  }
}

.practice-box {
  width: 100%;
  display: flex;
  justify-content: center;
  margin-top: 50rpx;
  margin-bottom: 16rpx;
}
</style>
