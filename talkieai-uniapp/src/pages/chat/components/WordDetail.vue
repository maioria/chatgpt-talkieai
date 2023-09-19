<template>
    <view class="word-detail-container">
        <LoadingRound v-if="wordDetailLoading"></LoadingRound>

        <!-- 单词内容 -->
        <view v-if="wordDetail">
            <LoadingRound v-if="practiceLoading"></LoadingRound>
            <Rate v-if="wordDetailAccuracyScore" :rate="wordDetailAccuracyScore" />
            <view class="original-word-box">
                <view class="left-box">
                    <view class="original-word-text">{{ wordDetail.original }}</view>
                    <audio-player class="audio-player-box" :content="wordDetail.original" :session-id="sessionId"></audio-player>
                </view>
                <view class="right-box">
                    <Collect type="WORD" :content="wordDetail.original"></Collect>
                </view>
            </view>
            <view class="phonetic-box">
                <view class="phonetic-text">
                    {{ wordDetail.phonetic }}
                </view>
            </view>
            <view class="translation-box">
                {{ wordDetail.translation }}
            </view>
        </view>

        <!-- 练习 -->
        <view class="speech-tip-box">
            练习
        </view>
        <Speech @success="handleSuccess"></Speech>
    </view>
</template>
<script setup lang="ts">
import { ref, defineEmits } from 'vue';
import chatRequest from '@/api/chat';
import AudioPlayer from '@/components/AudioPlayer.vue';
import LoadingRound from "@/components/LoadingRound.vue";
import Speech from '@/components/Speech.vue';
import Collect from '@/components/Collect.vue';
import Rate from '@/components/Rate.vue';

const wordDetailLoading = ref(false);
const practiceLoading = ref(false);
const wordDetailAccuracyScore = ref(null);
const wordDetail = ref(null);
const sessionId = ref('');
const emit = defineEmits();

const initData = (word: any, sessionIdVal: string) => {
    wordDetailAccuracyScore.value = word.accuracy_score;
    wordDetail.value = null;
    sessionId.value = sessionIdVal;
    wordDetailLoading.value = true;
    chatRequest.wordDetail({ word: word.word }).then((data) => {
        const wordDetailData = data.data;
        wordDetail.value = wordDetailData;
        wordDetailLoading.value = false;
    });
}

const handleSuccess = (data: any) => {
    if (!wordDetail.value) {
        return;
    }
    wordDetailAccuracyScore.value = null;
    wordDetailLoading.value = true;
    chatRequest.wordPractice({
        word: wordDetail.value.original,
        session_id: sessionId.value,
        file_name: data.fileName
    }).then((data) => {
        const wordDetailData = data.data;
        wordDetailAccuracyScore.value = wordDetailData.accuracy_score;
        wordDetailLoading.value = false;
    });
}
defineExpose({
    initData
});
</script>
<style lang="less" scoped>
.word-detail-container {
    .scrore-box {
        text-align: center;
    }

    .original-word-box {
        display: flex;
        justify-content: space-between;
        align-items: center;

        .left-box {
            display: flex;
            align-items: center;

            .original-word-text {
                font-size: 48rpx;
                font-weight: 600;
                line-height: 67rpx;
                letter-spacing: 1px;
            }

            .audio-player-box {
                margin-left: 32rpx;
            }
        }


    }

    .phonetic-box {
        margin-top: 18rpx;

        .phonetic-text {
            font-size: 28rpx;
            font-weight: 400;
            color: #707070;
            line-height: 40rpx;
        }
    }

    .translation-box {
        margin-top: 18rpx;
    }

    .speech-tip-box {
        width: 100%;
        display: flex;
        justify-content: center;
        margin-top: 50rpx;
        margin-bottom: 16rpx;
    }
}
</style>