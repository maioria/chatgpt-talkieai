<template>
  <uni-popup class="popup-container" ref="promotPopup" type="bottom" :background-color="popupBackgoundColor">
    <view class="promot-popup-container">
      <view @tap="handleClose" class="close-icon-box">
        <image class="close-icon" src="/static/icon_close.png"></image>
      </view>

      <view class="title-box">
        <view class="title"> 提示 </view>
      </view>
      <view class="sub-title-box">
        <view>您可以尝试说</view>
      </view>

      <!-- loading -->
      <loading-round class="loading-box" v-if="promptLoading"></loading-round>

      <!-- 提示内容 -->
      <view v-for="prompt in promoptList" :key="prompt.text">
        <view class="promot-box padding-left-right">
          <functional-text :session-id="sessionId" :text="prompt.text" :translate-show="prompt.translateShow"
            class="prompt-text-box"></functional-text>
          <view class="action-box">
            <view class="translate-icon-box left-box" :class="{ 'active': prompt.translateShow }">
              <image @tap="handleTranslatePrompt(prompt)" class="icon-tanslate" src="/static/icon_translate.png">
              </image>
            </view>
            <view @tap="sendMessage(prompt)" class="right-box"> 发送文本 </view>
          </view>
        </view>
        <view class="divide"></view>
      </view>

      <view class="speech-box">
        <speech :sessionId="sessionId" @success="handleSpeechSuccess"></speech>
      </view>
    </view>
  </uni-popup>
</template>
<script setup lang="ts">
import { ref, getCurrentInstance, onMounted } from "vue";
import FunctionalText from "@/components/FunctionalText.vue";
import Speech from "./MessageSpeech.vue";
import chatRequest from "@/api/chat";
import LoadingRound from "@/components/LoadingRound.vue";
import type { Prompt } from "@/models/models";

const promotPopup = ref<any>(null);
const sessionId = ref<any>(null);
const promptLoading = ref<boolean>(true);
const promoptList = ref<Prompt[]>([]);
const $bus: any = getCurrentInstance()?.appContext.config.globalProperties.$bus;
const popupBackgoundColor = ref("");

onMounted(() => {
  // 如果是微信息小程序，背景色要设置成#fff
  if (process.env.VUE_APP_PLATFORM === "mp-weixin") {
    popupBackgoundColor.value = "#fff";
  }
});

const handleClose = () => {
  closePopup();
};

const open = (sessionIdValue: string) => {
  sessionId.value = sessionIdValue;
  promotPopup.value.open();
  promptLoading.value = true;
  chatRequest
    .promptInvoke({
      session_id: sessionIdValue,
    })
    .then((data) => {
      promoptList.value = data.data.map((item: string) => {
        return {
          text: item,
          translateShow: false,
        };
      });
    }).finally(() => {
      promptLoading.value = false;
    })
};

const handleTranslatePrompt = (prompt: Prompt) => {
  prompt.translateShow = !prompt.translateShow;
};

const sendMessage = (prompt: Prompt) => {
  $bus.emit("SendMessage", {
    text: prompt.text,
  });
  closePopup();
};

const handleSpeechSuccess = () => {
  closePopup();
};

const closePopup = () => {
  console.log('closePopup')
  sessionId.value = '';
  promoptList.value = []
  promotPopup.value.close();
};

defineExpose({
  open,
});
</script>
<style lang="less" scoped>
.divide {
  width: 750rpx;
  height: 1rpx;
  // border: 1rpx solid #E8E8E8;
  background-color: #E8E8E8;
  margin-top: 27rpx;
}

.speech-divide-box {
  background-color: #FFF;
  padding-top: 156rpx;

  .speech-divide {
    width: 100%;
    height: 1rpx;
    box-shadow: 0rpx 0rpx 4rpx 0rpx rgba(0, 0, 0, 0.5);
    border: 1rpx solid #E5E5E5;
    filter: blur(4px);
  }
}


.padding-left-right {
  padding: 0 32rpx;
}

.padding-bottom {
  padding-bottom: 32rpx;
}

.speech-box {
  background-color: #fff;
  margin-top: 32rpx;
}

.promot-popup-container {
  background-color: #fff;
  position: relative;
  border-radius: 30rpx 30rpx 0 0;

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

  .title-box {
    padding: 32rpx 32rpx 0 32rpx;
    position: relative;

    &::after {
      position: absolute;
      content: "";
      background: #6236ff;
      width: 50rpx;
      height: 10rpx;
      border-radius: 5rpx;
      bottom: -12rpx;
      left: 50rpx;
    }

    .title {
      font-size: 42rpx;
      font-weight: 500;
    }
  }

  .sub-title-box {
    margin-top: 50rpx;
    padding: 0 32rpx 0 32rpx;
  }

  .sub-title {
    font-size: 28rpx;
  }

  .prompt-text-box {
    margin-top: 28rpx;
    display: flex;
  }

  .action-box {
    margin-top: 32rpx;
    display: flex;
    justify-items: center;
    align-items: center;
    justify-content: space-between;

    .right-box {
      color: #6236ff;
    }
  }

  .translate-icon-box {
    width: 32rpx;
    height: 32rpx;
    padding: 8rpx;
    display: flex;
    justify-content: center;
    border-radius: 4rpx;

    .icon-tanslate {
      width: 32rpx;
      height: 32rpx;
    }

    &.active {
      background: #e8ebff;
      color: #6236ff;
    }

  }

  .icon-tanslate {
    width: 32rpx;
    height: 32rpx;
  }
}

.loading-box {
  min-height: 100rpx;
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
}
</style>
