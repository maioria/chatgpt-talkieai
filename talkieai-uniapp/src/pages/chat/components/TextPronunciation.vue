<template>
    <view class="word-box">
        <view class="word-text" v-for="word in pronunciation.words" :key="word.word" @tap="handleWordDetail(word)"
            :class="{ incorrect: word.accuracy_score <= 60, good: word.accuracy_score > 60 && word.accuracy_score < 75 }">
            {{ word.word }}
        </view>
    </view>
</template>
<script setup lang="ts">
import { ref, defineEmits } from "vue";
import type { Pronunciation, Word } from '@/models/models';

const props = defineProps<{
    content: string,
    pronunciation: Pronunciation;
}>();
const emit = defineEmits();

const handleWordDetail = (word: Word) => {
    console.log(word)
    emit("wordClick", word);
};
</script>
<style lang="less" scoped>
.word-box {
    display: flex;
    font-size: 28rpx;
    flex-wrap: wrap;

    .word-text {
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