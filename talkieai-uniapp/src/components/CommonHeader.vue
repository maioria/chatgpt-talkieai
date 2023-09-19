<template>
  <view class="common-header"
    :style="{ height: CustomBar + 'px', backgroundColor: (backgroundColor ? backgroundColor : 'inhert') }">
    <view class="common-header-content" :style="style">
      <view class="left" @tap="handleBack">
        <slot name="left">
          <view class="left-icon-box">
            <image v-if="leftIcon" class="back-icon" src="/static/icon_header_back.png"></image>
          </view>
        </slot>
      </view>
      <view class="content">
        <slot name="content"></slot>
      </view>
      <view class="right">
        <!-- 小程序会有遮挡情况，不要使用 -->
        <slot name="right"></slot>
      </view>
    </view>
  </view>
</template>
<script setup lang="ts">
import {
  ref,
  defineProps,
  getCurrentInstance,
  computed,
  onMounted,
  inject,
} from "vue";
interface Props {
  leftIcon?: boolean;
  backFn?: () => void;
  backgroundColor?: string;
}

const CustomBar: any =
  getCurrentInstance()?.appContext.config.globalProperties.CustomBar;
const StatusBar: any =
  getCurrentInstance()?.appContext.config.globalProperties.StatusBar;
const props = defineProps<Props>();
const style = computed(
  () => `height:${CustomBar}px;padding-top:${StatusBar}px;`
);
const handleBack = () => {
  // 提高灵敏度，监听外层的返回事件，如果父组件未设置，逻辑不执行就可以
  if (!props.leftIcon) {
    return;
  }
  if (props.backFn) {
    props.backFn();
  } else {
    uni.navigateBack({
      delta: 1,
    });
  }
};
</script>
<style lang="less" scoped>
.common-header {
  top: 0;
  position: relative;

  .common-header-content {
    position: fixed;
    width: 100%;
    display: flex;
    padding: 0 32rpx;
    align-items: center;
    box-sizing: border-box;
    z-index: 100;
    background-color: inherit;

    .left {
      flex: 1;
      height: 100%;
      display: flex;
      justify-content: left;
      align-items: center;

      .left-icon-box {
        width: 48rpx;
        height: 48rpx;
        display: flex;
        justify-content: left;
        align-items: center;
      }

      .back-icon {
        width: 18rpx;
        height: 32rpx;
      }
    }

    .content {
      font-size: 36rpx;
      line-height: 50rpx;
      flex: 2;
      height: 100%;
      display: flex;
      justify-content: center;
      align-items: center;
    }

    .right {
      flex: 1;
      height: 100%;
      display: flex;
      justify-content: left;
      align-items: center;
      // 元素居右
      justify-content: flex-end;
    }
  }
}
</style>
