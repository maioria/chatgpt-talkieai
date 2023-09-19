<template>
  <uni-popup ref="translationPopup" type="bottom" :background-color="popupBackgoundColor">
    <view class="translation-container">
      <view @tap="handleClose" class="close-icon-box">
        <image class="close-icon" src="/static/icon_close.png"></image>
      </view>
      <view class="content">
        <view class="title-box">
          <text class="title-text"> 输入语句 </text>
        </view>
        <view class="textarea-box">
          <textarea v-model="inputText" confirm-type="send" class="textarea" placeholder="例如：我喜欢音乐"></textarea>
          <view @tap.stop="handleTranslate" class="translate-btn-box" :class="{ active: inputHasText }">
            <view class="translate-btn"> 翻译 </view>
          </view>
        </view>

        <!-- 翻译loading -->
        <view v-if="translating" class="loading-box">
          <LoadingRound />
        </view>
        <!-- 翻译后的文本 -->
        <view v-if="translationText" class="translation-box">
          <text class="translation-text">
            {{ translationText }}
          </text>
          <AudioPlayer class="playing-box" :content="translationText" :session-id="sessionId" />
        </view>
        <!-- 直接发送 -->
        <view v-if="translationText" class="send-box">
          <view class="send-btn-box">
            <view @tap="handleSend" class="send-btn"> 发送文本 </view>
          </view>
        </view>
      </view>
      <view class="speech-container">
        <Speech :sessionId="sessionId" @success="handleSuccess" />
      </view>
    </view>
  </uni-popup>
</template>
<script setup lang="ts">
import { ref, computed, getCurrentInstance, onMounted } from "vue";
import chatService from "@/api/chat";
import AudioPlayer from "@/components/AudioPlayer.vue";
import Speech from "./MessageSpeech.vue";
import LoadingRound from "@/components/LoadingRound.vue";

const $bus: any = getCurrentInstance()?.appContext.config.globalProperties.$bus;
const translationPopup = ref(null);
const inputText = ref("");
const translating = ref(false);
const translationText = ref("");
const sessionId = ref("");
const popupBackgoundColor = ref("");

onMounted(() => {
  // 如果是微信息小程序，背景色要设置成#fff
  if (process.env.VUE_APP_PLATFORM === "mp-weixin") {
    popupBackgoundColor.value = "#fff";
  }
});

// 是否已经输入文本
const inputHasText = computed(() => {
  return !!(inputText.value && inputText.value.trim());
});

const handleTranslate = () => {
  console.log("handleTransalte");
  if (!inputHasText.value) {
    uni.showToast({
      title: "请输入文本",
      icon: "none",
    });
    return;
  }
  translating.value = true;
  chatService
    .translateText({
      text: inputText.value,
      session_id: sessionId.value,
      target_language: "English",
    })
    .then((data) => {
      translationText.value = data.data;
      translating.value = false;
    })
    .catch(() => {
      translating.value = false;
    });
};

const handleSend = () => {
  if (!translationText.value) {
    uni.showToast({
      title: "请输入文本并进行翻译",
      icon: "none",
    });
    return;
  }
  $bus.emit("SendMessage", {
    text: translationText.value,
  });
  handleClose();
};

const handleSuccess = (data: any) => {
  handleClose();
};

const handleClose = () => {
  translationPopup.value.close();
  inputText.value = "";
  translationText.value = "";
  sessionId.value = "";
};

const open = (sessionIdVal: string) => {
  sessionId.value = sessionIdVal;
  translationPopup.value.open();
};

defineExpose({
  open,
  handleClose,
});
</script>
<style lang="less" scoped>
@import url("../../../less/global.less");

.translation-container {
  background-color: #fff;
  padding: 32rpx 32rpx 32rpx 32rpx;
  border-radius: 30rpx 30rpx 0px 0px;
  position: relative;

  .close-icon-box {
    position: absolute;
    padding: 32rpx;
    top: 0;
    right: 0;
    z-index: 99;
    line-height: 20rpx;

    .close-icon {
      width: 20rpx;
      height: 20rpx;
    }
  }

  .content {
    margin-top: 16rpx;
    background-color: #fff;

    .title-box {
      .title-text {
        width: 174rpx;
        height: 59rpx;
        font-size: 42rpx;
        font-weight: 500;
        color: #000000;
        line-height: 59rpx;
        letter-spacing: 1px;
      }
    }

    .textarea-box {
      margin-top: 50rpx;
      position: relative;

      .textarea {
        // 100%长度减去64rpx
        width: calc(100% - 64rpx);
        height: 350rpx;
        border: 1rpx solid #979797;
        padding: 28rpx;
      }

      .translate-btn-box {
        z-index: 100;
        position: absolute;
        bottom: 20rpx;
        right: 20rpx;
        width: 114rpx;
        height: 64rpx;
        border-radius: 10rpx;
        border: 1rpx solid #979797;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #979797;

        &.active {
          border: 1rpx solid #6236ff;
          color: #6236ff;
        }

        .translate-btn {
          width: 58rpx;
          height: 40rpx;
          font-size: 28rpx;
          font-weight: 400;
          line-height: 40rpx;
        }
      }
    }

    .translation-box {
      padding-top: 32rpx;
      display: flex;
      justify-content: flex-start;
      align-items: center;

      .translation-text {
        font-size: 28rpx;
        font-weight: 400;
        color: #000000;
        line-height: 40rpx;
        letter-spacing: 1px;
      }

      .playing-box {
        margin-left: 32rpx;
        width: 32rpx;
        height: 32rpx;
      }
    }
  }
}

.send-box {
  width: 100%;
  display: flex;
  justify-content: flex-end;
  margin-top: 36rpx;

  .send-btn-box {
    .send-btn {
      color: #6236ff;
    }
  }
}

.loading-box {
  min-height: 100rpx;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.speech-container {
  background-color: #fff;
  margin-top: 32rpx;
}
</style>
