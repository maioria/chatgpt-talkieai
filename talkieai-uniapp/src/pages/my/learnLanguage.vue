<template>
    <view class="container">
        <CommonHeader :leftIcon="redirectType !== 'init'" background-color="#F5F5FE">
            <template v-slot:content>
                <text></text>
            </template>
        </CommonHeader>
        <view class="learning-language-box">
            <view class="title">
                我想学...
            </view>
            <view class="content">
                <view v-for="language in languages" class="language-item" @click="selectLanguage(language)">
                    {{ language.label }}
                </view>
            </view>
        </view>
    </view>
</template>

<script setup lang="ts">
import CommonHeader from "@/components/CommonHeader.vue";
import { ref, onMounted } from "vue";
import sysRequest from '@/api/sys';
import accountRequest from '@/api/account';
import { onLoad } from "@dcloudio/uni-app";

const languages = ref([]);

onMounted(() => {
    sysRequest.getLanguages().then((data) => {
        languages.value = data.data;
    });
});

const selectLanguage = (language: any) => {
    accountRequest.setSettings({ target_language: language.value }).then((data) => {
        uni.navigateBack();
    });
};
</script>

<style scoped lang="less">
@import url('@/less/global.less');

.container {
    background-color: @common-bg-gray-color;

    .learning-language-box {
        margin: 0 48rpx;

        .title {
            background-color: @common-bg-gray-color;
            font-size: 42rpx;
            font-weight: 500;
            width: 100%;
            text-align: center;
            margin: 48rpx 0;
        }

        .content {
            .language-item {
                margin-top: 32rpx;
                border-radius: 20rpx;
                padding: 48rpx 32rpx;
                background-color: #fff;
                text-align: center;
                font-weight: 500;
                font-size: 36rpx;
            }
        }
    }

    padding-bottom: 100rpx;
}
</style>