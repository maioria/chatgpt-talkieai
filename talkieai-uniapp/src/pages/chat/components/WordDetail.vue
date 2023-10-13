<template>
    <view class="word-detail-container">
        <view>
            <!-- 发单 -->
            <LoadingRound v-if="practiceLoading"></LoadingRound>
            <template v-else-if="wordPronunciation">
                <Rate :rate="wordPronunciation.accuracy_score" />
                <view class="phoneme-box">
                    <PhonemeBox :word="wordPronunciation" @phonemeClick="handlePhonemeClick" />
                    <audio-player v-if="practiceFile" class="audio-player-box" :file-name="practiceFile"></audio-player>
                </view>
            </template>

            <!-- 单词内容 -->
            <LoadingRound v-if="wordDetailLoading"></LoadingRound>
            <template v-else-if="wordDetail">
                <view class="original-word-box">
                    <view class="left-box">
                        <view class="original-word-text">{{ wordDetail.original }}</view>
                        <audio-player class="audio-player-box" :content="wordDetail.original"
                            :session-id="sessionId"></audio-player>
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
            </template>
        </view>

        <!-- 练习 -->
        <view class="speech-tip-box">
            练习
        </view>
        <Speech @success="handleSuccess"></Speech>
    </view>
</template>
<script setup lang="ts">
import { ref } from 'vue';
import chatRequest from '@/api/chat';
import AudioPlayer from '@/components/AudioPlayer.vue';
import LoadingRound from "@/components/LoadingRound.vue";
import Speech from '@/components/Speech.vue';
import Collect from '@/components/Collect.vue';
import Rate from '@/components/Rate.vue';
import PhonemeBox from './PhonemeBox.vue';
import type { Word, Phoneme } from '@/models/models';

const wordDetailLoading = ref(false);
const practiceLoading = ref(false);
const wordDetailAccuracyScore = ref(null);
const wordPronunciation = ref<Word>();
const wordDetail = ref(null);
const sessionId = ref('');
const practiceFile = ref(null);

const initData = (word: Word, sessionIdVal: string) => {
    wordPronunciation.value = word;
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
    practiceLoading.value = true;
    practiceFile.value = null;
    chatRequest.wordPractice({
        word: wordDetail.value.original,
        session_id: sessionId.value,
        file_name: data.fileName
    }).then((res) => {
        const wordDetailData = res.data;
        wordPronunciation.value = wordDetailData['words'][0];
        practiceLoading.value = false;
        practiceFile.value = data.fileName;
    });
}

const handlePhonemeClick = (phoneme: Phoneme) => {
    console.log(phoneme)
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

    .phoneme-box {
        display: flex;
        justify-content: center;
        align-items: center;
        font-size: 36rpx;

        .audio-player-box {
            margin-left: 12rpx;
        }
    }
}
</style>