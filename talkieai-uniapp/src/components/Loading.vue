<template>
  <view class="loading-box">
    <view class="loading-box-content">
      <view class="loading-box-item loading-box-item0"></view>
      <view class="loading-box-item loading-box-item1"></view>
      <view class="loading-box-item loading-box-item2"></view>
    </view>
  </view>
</template>

<style lang="less" scoped>
.loading-box {
  position: relative;
  padding: 12px 24px;
  width: 80px;
  background: #f1f1f1;
  border-radius: 4px;
  overflow: hidden;
  box-sizing: border-box;
  .loading-box-content {
    display: flex;
    width: 32px;
    flex: 1;
  }
  .loading-box-item {
    display: block;
    width: 8px;
    height: 8px;
    background: #999;
    border-radius: 6px;
    margin-right: 4px;
    animation: bounce 1s infinite;
  }
  .loading-box-item1 {
    animation-delay: 0.2s;
  }
  .loading-box-item2 {
    animation-delay: 0.4s;
    margin-right: 0;
  }
}

@keyframes bounce {
  0% {
    display: none;
    opacity: 0.2;
  }
  50% {
    display: block;
    opacity: 1;
  }
  100% {
    display: none;
    opacity: 0.2;
  }
}
</style>
