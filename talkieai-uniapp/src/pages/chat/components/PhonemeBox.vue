<template>
<view class="phoneme-box">
        <view class="phoneme-text" v-for="(phoneme, index) in word.phonemes" :key="index" @tap="handlePhonemeDetail(phoneme)"
            :class="{ incorrect: phoneme.accuracy_score <= 60, good: phoneme.accuracy_score > 60 && phoneme.accuracy_score < 75 }">
            {{ phoneme.phoneme }}
        </view>
    </view>
</template>
<script setup lang="ts">
import { ref, defineEmits } from "vue";
import type { Word,Phoneme } from '@/models/models';

const props = defineProps<{
    word: Word;
}>();
const emit = defineEmits();

const handlePhonemeDetail = (phoneme: Phoneme) => {
    emit("phonemeClick", phoneme);
};
</script>
<style lang="less" scoped>
.phoneme-box {
    display: flex;
    font-size: 28rpx;
    flex-wrap: wrap;

    .phoneme-text {
        margin-left: 12rpx;

        &:first-child {
            margin-left: 0;
        }

        &.incorrect {
            color: #fc6262;
        }

        &.good {
            color: rgb(135, 98, 43);
        }
    }
}
</style>