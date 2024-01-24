<template>
  <view>
    <CommonHeader backgroundColor="#fff">
      <template v-slot:content>
        <text>Talkie</text>
      </template>
    </CommonHeader>
    <view class="content">
      <!-- 自由聊天 -->
      <view class="index-page-card">
        <view class="index-header-box">
          <image v-if="settingRole" :src="settingRole.role_image" class="index-header-img" />
        </view>
        <view class="intro-box">
          <view class="top-box">
            <view class="index-name">
              <text v-if="settingRole" class="index-name-text">{{ settingRole.local_name }}</text>
            </view>
            <view class="btn-box">
              <image src="/static/change.png" class="index-change-btn-icon" />
              <view @tap="goSwitchRole" class="index-change-btn">切换角色</view>
            </view>
          </view>
          <view class="intro-bottom-box">
            <view @tap="goChat" class="index-btn">进入会话</view>
          </view>
        </view>
      </view>

      <Topics class="topic-component" />
    </view>
  </view>
</template>

<script setup lang="ts">
import CommonHeader from "@/components/CommonHeader.vue";
import chatRequest from "@/api/chat";
import accountRequest from "@/api/account";
import Topics from "./components/Topics.vue";
import { onShow } from "@dcloudio/uni-app";
import { ref } from "vue";

const loading = ref(false);
const settingRole = ref(null);

onShow(() => {
  initData();
});
const initData = () => {
  loading.value = true;
  accountRequest.getRole().then((data) => {
    loading.value = false;
    const role_setting = data.data.role_setting;
    settingRole.value = role_setting
  });
};

const goSwitchRole = () => {
  uni.navigateTo({
    url: `/pages/index/switchRole`,
  });
};

const goChat = () => {
  // 检查是否有这个用户下的默认session，没有则创建一个新的
  chatRequest.sessionDefaultGet({}).then((data) => {
    if (data.data) {
      uni.navigateTo({
        url: `/pages/chat/index?sessionId=${data.data.id}`,
      });
    } else {
      chatRequest.sessionCreate({}).then((data) => {
        // 创建好session后会在首页面自动获取这个数据
        uni.navigateTo({
          url: `/pages/chat/index?sessionId=${data.data.id}`,
        });
      });
    }
  });
};
</script>
<style scoped lang="less">
@import url('@/less/global.less');

.content {
  margin: 0 32rpx;
  display: flex;
  flex-direction: column;
  align-items: center;

  .index-page-card {
    margin: 0 36rpx;
    width: 100%;
    height: 220rpx;
    background: linear-gradient(135deg, rgba(78, 79, 234, 0.97) 0%, rgba(213, 214, 232, 0.97) 100%);
    border-radius: 30rpx;
    padding: 30rpx 40rpx;
    display: flex;

    .index-header-box {
      width: 142rpx;
      height: 100%;
      display: flex;
      align-items: center;

      .index-header-img {
        width: 142rpx;
        height: 142rpx;
        border-radius: 71rpx;
        background: #333;
      }
    }

    .intro-box {
      flex: 1;
      height: 100%;
      margin-left: 28rpx;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      align-items: center;

      .top-box {
        display: flex;
        width: 100%;
        justify-content: space-between;

        .index-name {
          color: #fff;
          width: 140rpx;
          overflow: hidden;
          text-overflow: ellipsis;

          .index-name-text {
            font-size: 36rpx;
            font-weight: 400;
            color: #FFFFFF;
            line-height: 50rpx;
            letter-spacing: 1px;
            // 不换行，超出部分隐藏
            white-space: nowrap;
          }
        }

        .btn-box {
          display: flex;
          align-items: center;

          .index-change-btn-icon {
            width: 22rpx;
            height: 17rpx;
          }

          .index-change-btn {
            margin-left: 8rpx;
            color: #3E2792;
            font-size: 26rpx;
          }
        }
      }

      .intro-bottom-box {
        width: 340rpx;
        background: #5456EB;
        border-radius: 60rpx;
        height: 60rpx;
        display: flex;
        justify-content: center;
        align-items: center;

        .index-btn {
          font-size: 28rpx;
          font-weight: 400;
          color: #FFFFFF;
        }
      }
    }
  }

  .topic-component {
    width: 100%;
    margin-top: 50rpx;
  }
}
</style>