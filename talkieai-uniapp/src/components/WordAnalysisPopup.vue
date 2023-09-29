<template>
    <uni-popup ref="wordAnalysisPopup" type="bottom" :background-color="popupBackgoundColor">
        <view class="word-analysis-container">
            <view class="close-icon-box">
                <image @tap="handleClose" class="close-icon" src="/static/icon_close.png"></image>
            </view>
            <LoadingRound v-if="wordDetailLoading" :min-height="200"></LoadingRound>
            <view v-else-if="wordPhoneticSymbol" class="content">
                <view class="word-box row-bc">
                    <text class="word-text">{{ word }}</text>
                    <Collect type="WORD" :content="word" />
                </view>
                <view class="pronunciation-box row-sc">
                    <text class="pronunciation-text">{{ wordPhoneticSymbol }}</text>
                    <AudioPlayer class="pronunciation-play-icon" :content="word" />
                </view>
                <view class="translation-box row-bc">
                    <text class="translatetion-text">{{ wordExplain }}</text>
                </view>
            </view>
        </view>
    </uni-popup>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import AudioPlayer from '@/components/AudioPlayer.vue';
import LoadingRound from "@/components/LoadingRound.vue";
import chatRequest from '@/api/chat';
import Collect from '@/components/Collect.vue';
const app = getApp();

const word = ref('');
const wordAnalysisPopup = ref(null);
const wordPhoneticSymbol = ref(null);
const wordExplain = ref(null);
const wordDetailLoading = ref(false);
const popupBackgoundColor = ref("");

onMounted(() => {
    // 如果是微信息小程序，背景色要设置成#fff
    if (process.env.VUE_APP_PLATFORM === "mp-weixin") {
        popupBackgoundColor.value = "#fff";
    }
});

const handleClose = () => {
    wordAnalysisPopup.value.close();
    wordPhoneticSymbol.value = null;
    wordExplain.value = null;
};

const open = (wordText: string) => {
    word.value = wordText;
    wordDetailLoading.value = true;
    chatRequest.wordDetail({ word: wordText }).then((res) => {
        wordPhoneticSymbol.value = res.data.phonetic;
        wordExplain.value = res.data.translation;
        wordDetailLoading.value = false;
    });
    wordAnalysisPopup.value.open();
};

defineExpose({
    open,
    handleClose
});
</script>

<style lang="less" scoped>
@import url('@/less/global.less');

.word-analysis-container {
    background-color: #FFF;
    padding: 32rpx 32rpx 32rpx 32rpx;
    border-radius: 30rpx 30rpx 0 0;
    position: relative;

    .close-icon {
        position: absolute;
        top: 32rpx;
        right: 32rpx;
        width: 20rpx;
        height: 20rpx;
    }

    .content {
        margin-top: 16rpx;
        padding-top: 32rpx;
        background-color: #FFF;

        .word-box {
            margin-top: 16rpx;

            .word-text {
                font-size: 48rpx;
                word-break: break-all;
                color: #333;
                font-weight: 700;
            }
        }

        .pronunciation-box {
            margin-top: 16rpx;

            .pronunciation-text {
                font-weight: 700;
                color: #999;
            }

            .pronunciation-play-icon {
                margin-left: 16rpx;
            }
        }

        .translation-box {
            margin-top: 16rpx;
        }
    }
}
</style>