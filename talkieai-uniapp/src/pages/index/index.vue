<template>
  <view>
    <CommonHeader title="Talkie">
      <template v-slot:content>
        <text>Talkie</text>
      </template>
    </CommonHeader>
    <LoadingRound v-show="sessionLoading" />
    <view v-if="session" class="content">
      <view class="index-page-card">
        <view class="index-header-box">
          <image :src="session.teacher_avatar" class="index-header-img" />
        </view>
        <view class="index-name">
          <text class="index-name-text">{{ session.name }}</text>
        </view>
        <button @tap="goSwitchRole" class="index-change-btn">切换角色</button>
        <button @tap="goChat" class="common-button index-btn">进入会话</button>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
// import {useIndexInfo} from './hooks/index.hooks'
import CommonHeader from "@/components/CommonHeader.vue";
import LoadingRound from "@/components/LoadingRound.vue";

import { ref, onMounted } from "vue";
import { onShow, } from "@dcloudio/uni-app";
import chatRequest from "@/api/chat";

const session = ref(null);
const sessionLoading = ref(false);

onMounted(() => {
  uni.setNavigationBarTitle({
    title: "TalkieAI",
  });
});

onShow(() => {
  initData();
});

const initData = () => {
  sessionLoading.value = true;
  chatRequest.sessionDefaultGet({}).then((data) => {
    if (!data.data) {
      goSwitchRole();
    }
    sessionLoading.value = false;
    session.value = data.data;
  });
};

const goChat = () => {
  chatRequest.sessionDefaultGet({}).then((data) => {
    uni.navigateTo({
      url: `/pages/chat/index?sessionId=${session.value.id}`,
    });
  });
};

const goSwitchRole = () => {
  uni.navigateTo({
    url: `/pages/home/index`,
  });
};
</script>

<style scoped src="./less/index.less" lang="less"></style>
