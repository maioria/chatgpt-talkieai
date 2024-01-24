<template>
  <!-- 语法评估 -->
  <view class="grammar-box">
    <loading-round v-if="grammarAnalysisLoading" />
    <view v-if="!grammarAnalysisLoading && grammarAnalysisResult" class="grammar-content">
      <view v-if="grammarAnalysisResult.is_correct" class="handclap-box">
        <view class="handclap-text">Well done！</view>
      </view>
      <template v-else>
        <view class="tips-box">
          <image class="grammar-icon-tips" src="/static/icon_incorrect.png"></image>
          <view class="grammar-result-content red">{{ grammarAnalysisResult.original }}</view>
        </view>
        <view class="line"><!----></view>
        <view class="tips-box">
          <image class="grammar-icon-tips" src="/static/icon_correct.png"></image>
          <view class="grammar-result-content green">
            {{ grammarAnalysisResult.correct_content }}
          </view>
        </view>
      </template>
      <view v-if="grammarAnalysisResult.error_reason" class="reason-box">
        <view class="error-tips sub-title">
          错误点
        </view>
        <view class="reason">
          {{ grammarAnalysisResult.error_reason }}
        </view>
      </view>
      <view v-if="grammarAnalysisResult.better" class="reason-box">
        <view class="">
          <view class="sub-title">你也可以说</view>
        </view>
        <functional-text class="reason" :text="grammarAnalysisResult.better" :wordClickable="false" :sessionId="sessionId"
          :translateShow="translateBetterContentShow" />

        <view class="action-box">
          <view class="translate-icon-box icon-box">
            <image class="translate-icon icon" @tap="handleTranlate(grammarAnalysisResult.better)"
              src="/static/icon_translate.png"></image>
          </view>
          <view class="collect-icon-box icon-box">
            <collect type="SENTENCE" :content="grammarAnalysisResult.better"></collect>
          </view>
          <view class="copy-icon-box icon-box">
            <image @tap="handleCopy(grammarAnalysisResult.better)" class="copy-icon icon"
              src="/static/icon_copy_text.png"></image>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>
<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import FunctionalText from '@/components/FunctionalText.vue';
import LoadingRound from "@/components/LoadingRound.vue";
import Collect from '@/components/Collect.vue';
import chatRequest from '@/api/chat';

const props = defineProps<{
  sessionId: string;
  messageId: string;
}>();

const grammarAnalysisLoading = ref(false);
const grammarAnalysisResult = ref(null);
const translateBetterContentShow = ref(false);

onMounted(() => {

});

const initData = () => {
  console.log(props.sessionId)
  if (grammarAnalysisResult.value) {
    return;
  }
  grammarAnalysisLoading.value = true;
  chatRequest.grammarInvoke({ message_id: props.messageId }).then((data) => {
    grammarAnalysisLoading.value = false;
    grammarAnalysisResult.value = data.data;
  });
};

const handleTranlate = (message: string) => {
  translateBetterContentShow.value = !translateBetterContentShow.value;
};

const handleCopy = (message: string) => {
  uni.setClipboardData({
    data: message,
    success: () => uni.showToast({ title: '复制成功' }),
    fail: () => uni.showToast({ title: '复制失败', icon: 'none' })
  });
};

defineExpose({
  initData
});
</script>
<style lang="scss" scoped>
.grammar-box {
  padding-top: 12rpx;
  padding-bottom: 350rpx;
  min-height: 300rpx;

  .grammar-content {
    .handclap-box {
      display: flex;
      justify-content: center;
      align-items: center;

      .handclap-text {
        font-size: 28rpx;
        font-weight: 400;
        color: #49CEB0;
        line-height: 40rpx;
      }
    }
  }

  .action-box {
    display: flex;
    margin-top: 30rpx;

    .icon-box {
      margin-left: 24rpx;

      &:first-child {
        margin-left: 0;
      }
    }

    .icon {
      width: 32rpx;
      height: 32rpx;
    }
  }

  .tips-box {
    margin-top: 24rpx;
    display: flex;
    align-items: center;

    .grammar-icon-tips {
      width: 24rpx;
      height: 24rpx;
      margin-right: 24rpx;
    }

    .grammar-result-content {
      padding: 24rpx;
      border-radius: 4rpx;
      flex: 1;

      &.red {
        background-color: rgba(255, 243, 243, 1);
      }

      &.green {
        background-color: rgba(230, 244, 240, 1);
      }
    }

  }
}

.sub-title {
  height: 40rpx;
  font-size: 28rpx;
  line-height: 40rpx;
  padding: 40rpx 0;
}

.reason {
  line-height: 40rpx;
  font-size: 28rpx;
  font-weight: 400;
}

.better-content-box {
  display: flex;
  gap: 24rpx;

  .better-content-icon {
    width: 32rpx;
    height: 32rpx;
  }
}
</style>