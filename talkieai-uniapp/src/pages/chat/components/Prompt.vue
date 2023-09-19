<template>
    <view class="menu-container">
        <view @tap="handlePrompt" class="menu-item">
            <image class="menu-icon" src="/static/icon_prompt.png"></image>
            <view class="menu-text">
                提示
            </view>
        </view>
        <view @tap="handleTranslate" class="menu-item">
            <image class="menu-icon" src="/static/icon_translate.png"></image>
            <view class="menu-text">
                翻译
            </view>
        </view>
        <PromptPopup ref="promotPopupRef"></PromptPopup>
        <TranslationPopup ref="translationPopupRef"></TranslationPopup>
    </view>
</template>
<script setup lang="ts">
import { ref } from 'vue';
import PromptPopup from './PromptPopup.vue';
import TranslationPopup from './TranslationPopup.vue';

const latestMessageId = ref<string>(''); // Set the appropriate default value
const promotPopupRef = ref(null);
const translationPopupRef = ref(null);

const props = defineProps<{
    sessionId?: string;
}>()

const handlePrompt = () => {
    promotPopupRef.value.open(props.sessionId);
};

const handleTranslate = () => {
    translationPopupRef.value.open(props.sessionId);
};
</script>
<style scoped lang="less">
.menu-container {
    display: flex;
    padding: 12rpx 32rpx;
    background-color: #FFF;

    .menu-item {
        background-color: rgba(242, 242, 242, 1);
        border-radius: 14rpx;
        display: flex;
        align-items: center;
        padding: 9rpx 18rpx;
		margin-left: 36rpx;

		&:first-child {
		  margin-left: 0;	
		}

        .menu-icon {
            width: 32rpx;
            height: 32rpx;
        }

        .menu-text {
            margin-left: 14rpx;
        }
    }
}
</style>