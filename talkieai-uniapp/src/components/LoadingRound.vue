<template>
  <view class="loading-round" :style="containerStyle">
    <image class="loading-round-img" src="/static/loading.png"></image>
  </view>
</template>
<script setup lang="ts">
import {
  ref,
  defineProps,
  computed
} from 'vue';
interface Props {
  minHeight?: number;
}
const props = defineProps<Props>();
const containerStyle = computed(
  () => {
    if (props.minHeight) {
      return `min-height:${props.minHeight}rpx;`
    }
    return '';
  }
);
</script>
<style lang="less" scoped>
.loading-round {
  display: flex;
  align-items: center;
  justify-content: center;

  .loading-round-img {
    width: 16px;
    height: 16px;
    animation: running 0.6s infinite;
  }
}

@keyframes running {
  0% {
    transform: rotate(40deg);
  }

  33% {
    transform: rotate(150deg);
  }

  67% {
    transform: rotate(230deg);
  }

  100% {
    transform: rotate(360deg);
  }
}
</style>
