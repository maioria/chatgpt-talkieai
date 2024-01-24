<template>
  <view>
    <CommonHeader title="Talkie">
      <template v-slot:content>
        <text>练习</text>
      </template>
    </CommonHeader>
    <view class="content">
      <view class="chat-tab-box">
        <view :class="`chat-tab ${tabNum === '1' ? 'chat-tab-actice' : ''}`" @tap="tabChange('1')">单词</view>
        <view :class="`chat-tab ${tabNum === '2' ? 'chat-tab-actice' : ''}`" @tap="tabChange('2')">句子</view>
      </view>
      <view class="chat-tab-content">
        <scroll-view scroll-y="true" id="chat-tab-content-one"
          :class="`chat-tab-content-one ${tabNum === '2' ? 'chat-tab-content-one_hidden' : ''}`"
          @scrolltolower="onScroll">
          <Single @deleteCollect="handleDeleteCollect" v-for="word in wordList" :collect="word" />
          <loading-round v-if="wordLoading" />
        </scroll-view>
        <scroll-view scroll-y="true" id="chat-tab-content-two"
          :class="`chat-tab-content-two ${tabNum === '1' ? 'chat-tab-content-two_hidden' : ''}`"
          @scrolltolower="onScroll">
          <Statement v-for="sentence in sentenceList" :collect="sentence" :cannotCancel="false" />
          <loading-round v-if="sentenceLoading" />
        </scroll-view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from "vue";
import { onShow } from "@dcloudio/uni-app";

import LoadingRound from "@/components/LoadingRound.vue";
import CommonHeader from "@/components/CommonHeader.vue";
import type { Collect } from "@/models/models";
import Single from "./components/Single.vue";
import Statement from "./components/Statement.vue";
import accountRequest from "@/api/account";
const wordList = ref<Collect[]>([]);
const sentenceList = ref<Collect[]>([]);
const tabNum = ref<string>("1");
const wordPageSize = ref<number>(1);
const senPageSize = ref<number>(1);
const wordLoading = ref<boolean>(false);
const sentenceLoading = ref<boolean>(false);

onMounted(() => {
  uni.setNavigationBarTitle({
    title: 'TalkieAI'
  });
});

onShow(() => {
  nextTick(() => {
    initData();
  });
});

const handleDeleteCollect = (id: number) => {
  initData();
};

const initData = () => {
  wordPageSize.value = 1;
  senPageSize.value = 1;
  wordList.value = [];
  sentenceList.value = [];
  getWord();
  getSen();
}

const refreshData = () => {
  wordPageSize.value = 1;
  senPageSize.value = 1;
  getWord();
  getSen();
}

const getWord = () => {
  if (wordLoading.value) return;
  wordLoading.value = true;
  let params = {
    page: wordPageSize.value,
    page_size: 10,
    type: "WORD",
  };
  accountRequest.collectsGet(params).then((data) => {
    wordList.value = wordList.value.concat(data.data.list);
  });
  wordLoading.value = false;
};

const getSen = () => {
  if (sentenceLoading.value) return;
  sentenceLoading.value = true;
  let params = {
    page: senPageSize.value,
    type: "SENTENCE",
  };
  accountRequest.collectsGet(params).then((data) => {
    sentenceList.value = sentenceList.value.concat(data.data.list);
  });
  sentenceLoading.value = false;
};

const tabChange = (type: "1" | "2") => {
  tabNum.value = type;
};
const onScroll = (event: any) => {
  if (tabNum.value === "1") {
    wordPageSize.value = wordPageSize.value + 1;
    getWord();
  } else {
    senPageSize.value = senPageSize.value + 1;
    getSen();
  }
};
</script>

<style lang="scss">
.content {
  display: flex;
  flex-direction: column;
}

.goods-carts {
  /* #ifndef APP-NVUE */
  display: flex;
  /* #endif */
  flex-direction: column;
  position: fixed;
  left: 0;
  right: 0;
  /* #ifdef H5 */
  left: var(--window-left);
  right: var(--window-right);
  /* #endif */
  bottom: 0;
}

.logo {
  height: 200rpx;
  width: 200rpx;
  margin-top: 200rpx;
  margin-left: auto;
  margin-right: auto;
  margin-bottom: 50rpx;
}

.text-area {
  display: flex;
  justify-content: center;
}

.title {
  font-size: 36rpx;
  color: #8f8f94;
}

.chat-tab-content {
  overflow-x: hidden;
}

.chat-tab-content-one {
  left: 0vw;
  position: absolute;
  width: 100vw;
  transition: 0.3s all linear;
  overflow-y: auto;
  height: calc(100vh - 340rpx);
}

.chat-tab-content-one_hidden {
  left: -100vw;
}

.chat-tab-content-two {
  left: 0vw;
  position: absolute;
  width: 100vw;
  transition: 0.3s all linear;
  overflow-y: auto;
  height: calc(100vh - 340rpx);
}

.chat-tab-content-two_hidden {
  left: 100vw;
}

.chat-tab-box {
  display: flex;
  padding: 32rpx;
  align-items: center;

  .chat-tab {
    margin-right: 44rpx;
    font-size: 36rpx;
    position: relative;
    display: flex;
    justify-content: center;
    transition: 0.1s all linear;
    height: 50rpx;
    line-height: 50rpx;
  }

  .chat-tab-actice {
    font-size: 42rpx;
    font-weight: 500;
  }

  .chat-tab-actice::after {
    position: absolute;
    content: "";
    background: #6236ff;
    width: 40rpx;
    height: 10rpx;
    border-radius: 5rpx;
    bottom: -20rpx;
  }
}
</style>
