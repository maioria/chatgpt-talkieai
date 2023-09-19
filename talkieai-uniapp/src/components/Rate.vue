<template>
  <view class="rate-container">
    <view v-if="rate && rate > 0">
      <SeekBar :width="140" :processVal="rate"></SeekBar>
    </view>
  </view>
</template>
<script setup lang="ts">
import { ref, onMounted } from "vue";
import SeekBar from "./Rare2.vue";

const props = defineProps<{
  rate: number;
}>();

onMounted(() => {});
</script>
<style scoped lang="less">
.rate-container {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
}
.rate-box {
  width: 300rpx;
  height: 300rpx;
  background: #333;
  padding: 20rpx;
  border-radius: 200rpx;
  box-sizing: border-box;
}
.rate-small-box {
  width: 260rpx;
  height: 260rpx;
  background: #eee;
  border-radius: 130rpx;
  box-sizing: border-box;
}
</style>
