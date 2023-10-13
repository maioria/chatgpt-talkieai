<template>
    <uni-popup @change="handlePopupChange" ref="grammarPopup" type="bottom" :background-color="popupBackgoundColor">
        <view class="message-grammat-container">
            <view @tap="handleClose" class="close-icon-box">
                <image class="close-icon" src="/static/icon_close.png"></image>
            </view>
            <view v-if="wordDetailShow" @tap="handleCloseWordDetail" class="word-back-icon-box">
                <image class="icon" src="/static/icon_header_back.png"></image>
            </view>
            <view v-if="!wordDetailShow" class="tab-box">
                <view @tap="handleActive('grammar')" class="tab-item" :class="{ 'active': activeView === 'grammar' }">
                    语法
                </view>
                <view @tap="handleActive('pronunciation')" class="tab-item"
                    :class="{ 'active': activeView === 'pronunciation' }">
                    发音
                </view>
            </view>

            <!-- 单个单词评分 -->
            <WordDetail v-if="wordDetailShow" ref="wordDetailRef"></WordDetail>

            <!-- 语法评估 -->
            <MessageGrammar v-if="activeView === 'grammar' && !wordDetailShow" class="grammar-box" :message-id="messageId"
                :session-id="sessionId" ref="messageGrammarRef" />

            <!-- 发音评估 -->
            <MessagePronunciation v-if="activeView === 'pronunciation' && !wordDetailShow" :message-id="messageId"
                :session-id="sessionId" :message-content="messageContent" :file-name="fileName" @wordClick="handleWordClick"
                ref="messagePronunciationRef"></MessagePronunciation>
        </view>
    </uni-popup>
</template>
<script setup lang="ts">
import { ref, reactive, nextTick, onMounted } from 'vue';
import MessageGrammar from './MessageGrammar.vue';
import MessagePronunciation from './MessagePronunciation.vue';
import WordDetail from './WordDetail.vue';
import type { Word } from '@/models/models';


const grammarPopup = ref(null);
const sessionId = ref('');
const messageId = ref('');
const messageContent = ref('');
const fileName = ref('');

const activeView = ref('grammar');
const grammarAnalysisResult = ref(null);
const pronunciationResult = ref(null);
const wordDetailShow = ref(false);
const messageGrammarRef = ref(null);
const messagePronunciationRef = ref(null);
const wordDetailRef = ref(null);
const popupBackgoundColor = ref("");

onMounted(() => {
    // 如果是微信息小程序，背景色要设置成#fff
    if (process.env.VUE_APP_PLATFORM === "mp-weixin") {
        popupBackgoundColor.value = "#fff";
    }
});

const handleCloseWordDetail = () => {
    wordDetailShow.value = false;
    initData();
};

const handleWordDetail = (word: Word) => {
    wordDetailShow.value = true;

    nextTick(() => {
        setTimeout(() => {
            wordDetailRef.value.initData(word, sessionId.value);
        }, 100);
    });
};

const handlePopupChange = ({ show, type }) => {

};

const handleActive = (active: string) => {
    activeView.value = active;
    initData();
};

const initData = () => {
    // ref会加载不及时
    setTimeout(() => {
        if (activeView.value === 'pronunciation') {
            nextTick(() => {
                messagePronunciationRef.value.initData();
            });
        } else {
            nextTick(() => {
                messageGrammarRef.value.initData();
            });
        }
    }, 100);
};

const handleClose = () => {
    grammarPopup.value.close();
    activeView.value = 'grammar';
    wordDetailShow.value = false;
};


const open = (id: string, content: string, file: string, sessionIdVal: string, type: string|undefined) => {
    messageId.value = id;
    sessionId.value = sessionIdVal
    messageContent.value = content;
    fileName.value = file;
    if (type && type==='pronunciation') {
        activeView.value = 'pronunciation';
    } else {
        activeView.value = 'grammar';
    }
    grammarPopup.value.open();

    nextTick(() => {
        setTimeout(() => {
            if (activeView.value === 'pronunciation') {
                messagePronunciationRef.value.initData();
            } else {
                messageGrammarRef.value.initData();
            }
        }, 100);
    });
};

const handleWordClick = (word: Word) => {
    handleWordDetail(word);
};

defineExpose({
    open,
    handleClose
});
</script>
<style lang="scss" scoped>
.message-grammat-container {
    background-color: #FFF;
    padding: 32rpx;
    position: relative;

    .close-icon-box {
    position: absolute;
    padding: 32rpx;
    top: 0;
    right: 0;
    z-index: 99;
    line-height: 20rpx;

    .close-icon {
      width: 20rpx;
      height: 20rpx;
    }
  }

    .tab-box {
        display: flex;
        align-items: center;
        margin-bottom: 48rpx;

        .tab-item {
            margin-left: 42rpx;
            position: relative;
            display: flex;
            justify-content: center;
            height: 50rpx;
            font-size: 36rpx;
            font-weight: 400;
            line-height: 50rpx;

            &:first-child {
                margin-left: 0;
            }

            &.active {
                height: 59rpx;
                font-size: 42rpx;
                font-weight: 500;
                color: #000000;
                line-height: 59rpx;

                &::after {
                    position: absolute;
                    content: "";
                    background: #6236ff;
                    width: 40rpx;
                    height: 10rpx;
                    border-radius: 5rpx;
                    bottom: -20rpx;
                }
            }
        }
    }

    .grammar-box {
        padding-top: 12rpx;
    }
}

.word-back-icon-box {
    width: 18rpx;
    height: 32rpx;

    .icon {
        width: 18rpx;
        height: 32rpx;
    }
}
</style>