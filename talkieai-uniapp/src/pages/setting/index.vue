<template>
  <view>
    <CommonHeader :leftIcon="true" :back-fn="handleBackPage" title="Talkie">
      <template v-slot:content>
        <text>设置</text>
      </template>
    </CommonHeader>
    <view class="mine-content">
      <view class="setting">
        <view class="setting-card">
          <text class="setting-card-title">自动播放语音</text>
          <Checkbox @input="(check) => inputCheck('auto_playing_voice', check)"
            :checked="settingInfo.auto_playing_voice" />
        </view>
        <view class="setting-card">
          <text class="setting-card-title">自动模糊文本</text>
          <Checkbox @input="(check) => inputCheck('auto_text_shadow', check)" :checked="settingInfo.auto_text_shadow" />
        </view>
        <view class="setting-card">
          <text class="setting-card-title">自动语音评分</text>
          <Checkbox @input="(check) => inputCheck('auto_pronunciation', check)"
            :checked="settingInfo.auto_pronunciation" />
        </view>
      </view>
      <view class="setting-bot">
        <text class="setting-card-title">语速</text>
        <view class="tab-box">
          <view :class="`tab-item ${selectTabId == '0' ? 'tab-item-select' : ''}`" @tap="selectTab('0')">
            <text>慢速</text>
          </view>
          <view :class="`tab-item ${selectTabId == '1' ? 'tab-item-select' : ''}`" @tap="selectTab('1')">
            <text>正常</text>
          </view>
          <view :class="`tab-item ${selectTabId == '2' ? 'tab-item-select' : ''}`" @tap="selectTab('2')">
            <text>较快</text>
          </view>
        </view>
        <button @tap="deleteAllMessages" class="common-button setting-clear">
          清空聊天记录
        </button>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import CommonHeader from "@/components/CommonHeader.vue";
import Checkbox from "../../components/Checkbox.vue";
import { ref, reactive, onMounted, watch } from "vue";
import accountRequest from "@/api/account";
import chatRequest from "@/api/chat";
const selectTabId = ref<string>("1");
const settingInfo = ref<any>({});
const formInfo = ref<any>({});

// Todo 需要在设置值变化时调用后台进行更新，设置完后chat页面能实时获取更新数据

onMounted(() => {
  uni.setNavigationBarTitle({
    title: 'TalkieAI'
  });
  accountRequest.settingsGet().then((data) => {
    if (data.code === "200") {
      settingInfo.value = data.data;
      if (data.data.playing_voice_speed) {
        selectTabId.value = data.data.playing_voice_speed;
      } else {
        selectTabId.value = "1";
      }
      formInfo.value = data.data;
    }
  });
});

const settingFunction = (params: any) => {
  accountRequest.settingsPost(params).then((data) => {
    console.log(data);
    if (data.code === "200") {
      console.log("设置成功");
    }
  });
};

/**
 * 回到主页面
 */
const handleBackPage = () => {
  // uni.switchTab({
  //   url: "/pages/my/index",
  // });
  uni.navigateBack({
    delta: 1,
  });
};

const selectTab = (id: string) => {
  selectTabId.value = id;
};

const inputCheck = (type: string, check: boolean) => {
  settingInfo.value = {
    ...settingInfo.value,
    [type]: check,
  };
  let params = {
    ...settingInfo.value,
    playing_voice_speed: selectTabId.value,
  };
  settingFunction(params);
};

const deleteAllMessages = () => {
  uni.showModal({
    title: "提示",
    content: "确定清空聊天记录吗？",
    success: function (res) {
      if (res.confirm) {
        console.log("用户点击确定");
        chatRequest.sessionDefaultGet({}).then((data) => {
          chatRequest.messagesAllDelete(data.data.id).then((data) => {
            console.log(data);
            uni.showToast({
              title: "清空成功",
              icon: "none",
            });
          });
        });
      } else if (res.cancel) {
        console.log("用户点击取消");
      }
    },
  });
};

watch(
  () => selectTabId,
  (newVal) => {
    if (newVal) {
      let params = {
        ...settingInfo.value,
        playing_voice_speed: selectTabId.value,
      };
      settingFunction(params);
    }
  },
  { deep: true }
);
</script>
<style lang="less">
.common-switch {
  .uni-switch-input {
    border-color: #5d33f9;
    background-color: #5d33f9;
  }
}
</style>
<style scoped src="./less/index.less" lang="less"></style>
