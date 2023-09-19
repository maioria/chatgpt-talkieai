<template>
  <view class="container">
    <CommonHeader
      :left-icon="true"
      style="background-color: none; color: #fff"
      :back-fn="handleBackPage"
      title="聊天"
    >
      <template v-slot:left>
        <image
          @tap="handleBackPage"
          class="back-icon"
          src="/static/icon_home.png"
        ></image>
      </template>
      <template v-slot:content>
        <view>选择角色</view>
      </template>
    </CommonHeader>
    <view class="content">
      <!-- <view class="index-change-position-one"></view> -->

      <!-- <view class="index-change-position-two"></view> -->
      <view class="language-picker-container">
        <view class="language-picker-box">
          <picker
            class="language-picker"
            mode="multiSelector"
            @change="handleLanguageChange"
            @columnchange="handleLanguageColumnChange"
            :range="languageRange"
          >
            <view class="picker">
              <text class="picker-label">
                {{ languageLabel }}
              </text>
              <image
                class="icon-down-arrow"
                src="/static/icon_down_white.png"
              />
            </view>
          </picker>
        </view>
      </view>
      <swiper
        class="swiper"
        circular
        :indicator-dots="true"
        :autoplay="false"
        :interval="interval"
        :duration="duration"
        @change="swiperChange"
      >
        <swiper-item v-for="m in roles" :key="m.id" class="index-page-card-box">
          <view class="index-page-card">
            <view class="index-header-box">
              <image :src="m.avatar" class="index-header-img" />
            </view>
            <view class="index-name">
              <text class="index-name-text">{{ m.local_name }}</text>
              <AudioPlayer
                :content="audioPlayerContent"
                :speech_role_name="m.short_name"
              />
            </view>
            <!-- <view class="style-box">
              <view v-for="style in m.role_styles" class="style-text">
                {{ style }}
              </view>
            </view> -->
          </view>
        </swiper-item>
      </swiper>
      <button @tap="createSession" class="common-button index-btn">
        进入会话
      </button>
    </view>
  </view>
</template>

<script setup lang="ts">
import CommonHeader from "@/components/CommonHeader.vue";
import AudioPlayer from "@/components/AudioPlayer.vue";
import { ref, onMounted, computed } from "vue";
import type { Language, Role } from "./model";
import roleRequest from "./service";
import chatRequest from "@/api/chat";
import languageGroupList from "./components/language";

const languages = ref<Language[]>([]);
const roles = ref<Role[]>([]);
const duration = ref<number>(500);
const interval = ref<number>(2000);
const selectIndex = ref<number>(0);
const audioPlayerContent = ref<string>("");

const selectedLanguageIndex = ref<number[]>([0, 0]);
const languageRange = ref<any[]>([]);

const languageLabel = computed(() => {
  if (!languageRange.value || languageRange.value.length === 0) {
    return "";
  }
  console.log(languageRange.value);
  console.log(selectedLanguageIndex.value);
  return `${languageRange.value[1][selectedLanguageIndex.value[1]]}`;
});

onMounted(() => {
  initAudioPlayerContent();
  initLanguages();
  uni.setNavigationBarTitle({
    title: "TalkieAI",
  });
});
const initLanguages = () => {
  const languageList = languageGroupList.map((item: any) =>
    removeParentheses(item.label)
  );
  const countryLabelList = languageGroupList[0].list.map(
    (item: any) => item.label
  );
  languageRange.value = [languageList, countryLabelList];

  initRoles();
};

/**
 * 确认语言，加载角色
 */
const handleLanguageChange = (e: any) => {
  initRoles();
  initAudioPlayerContent();
};

const handleLanguageColumnChange = (e: any) => {
  selectedLanguageIndex.value[e.detail.column] = e.detail.value;
  if (e.detail.column === 0) {
    initLanguageLabelRange();
    selectedLanguageIndex.value[1] = 0;
  }
};

const initLanguageLabelRange = () => {
  const languageList = languageGroupList.map((item) =>
    removeParentheses(item.label)
  );
  const countryLabelList = languageGroupList[
    selectedLanguageIndex.value[0]
  ].list.map((item: any) => item.label);
  languageRange.value = [languageList, countryLabelList];
};

const removeParentheses = (str: string) => {
  // 匹配最后一对括号及其内容的正则表达式
  const regex = /\([^()]*\)$|\（[^()]*\）$/;

  // 使用空字符串替换匹配到的内容
  return str.replace(regex, "");
};
const initAudioPlayerContent = () => {
  roleRequest
    .languageExampleGet({
      language:
        languageGroupList[selectedLanguageIndex.value[0]].list[
          selectedLanguageIndex.value[1]
        ].key,
    })
    .then((data) => {
      audioPlayerContent.value = data.data;
    });
};
const initRoles = () => {
  roleRequest
    .rolesGet({
      locale:
        languageGroupList[selectedLanguageIndex.value[0]].list[
          selectedLanguageIndex.value[1]
        ].key,
    })
    .then((data) => {
      roles.value = data.data;
    });
};

const swiperChange = (info: any) => {
  selectIndex.value = info.detail.current;
};
// 创建会话
const createSession = () => {
  let role = roles.value[selectIndex.value];
  chatRequest.sessionCreate({ role_name: role.short_name }).then((data) => {
    // 创建好session后会在首页面自动获取这个数据
    uni.redirectTo({
      url: `/pages/chat/index?sessionId=${data.data.id}`,
    });
  });
};
/**
 * 回到主页面
 */
const handleBackPage = () => {
  uni.switchTab({
    url: "/pages/index/index",
  });
};
</script>

<style scoped src="./less/index.less" lang="less"></style>
<style lang="less">
.uni-picker-action.uni-picker-action-confirm {
  color: rgba(95, 96, 235, 1) !important;
}
.uni-swiper-dots-horizontal {
  bottom: 200px !important;
}

.back-icon {
  width: 48rpx;
  height: 48rpx;
}
.index-name {
  display: flex;
  align-items: center;
}

.language-picker-container {
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;

  .language-picker-box {
    width: 590rpx;
    background: linear-gradient(
      135deg,
      rgba(255, 255, 255, 0.1) 0%,
      rgba(255, 255, 255, 0.2) 100%
    );
    border-radius: 64rpx;
    border: 1rpx solid #979797;
    padding: 28rpx 36rpx;
    display: flex;
    justify-content: space-between;
    align-items: center;

    .language-picker {
      display: flex;
      width: 100%;
      justify-content: space-between;
      align-items: center;

      .picker {
        width: 518rpx;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 36rpx;
        font-weight: 400;
        color: #ffffff;
        letter-spacing: 1px;

        .icon-down-arrow {
          width: 32rpx;
          height: 18rpx;
          margin-left: 16rpx;
        }
      }
    }
  }
}
</style>
