<template>
    <view class="container">
        <CommonHeader :leftIcon="true" :backFn="handleBackFn" backgroundColor="#F5F5FE">
            <template v-slot:content>
                <text>完成情况</text>
            </template>
        </CommonHeader>
        <view class="content">
            <template v-if="topicHistory">
                <view class="completion-title-box">
                    <image class="completion-icon" src="/static/topic-result-pass.png" mode="heightFix" />
                    <view class="completion-title">已完成</view>
                </view>
                <view class="completion-container">
                    <view class="complete-item">
                        <view class="item-data">
                            {{ topicHistory.main_target_completed_count + topicHistory.trial_target_completed_count }}/{{
                                topicHistory.main_target_count + topicHistory.trial_target_count }}
                        </view>
                        <view class="item-title">已达成目标</view>
                    </view>
                    <view class="complete-item">
                        <view class="item-data">{{ topicHistory.content_score }}%</view>
                        <view class="item-title">分数</view>
                    </view>
                    <view class="complete-item">
                        <view class="item-data">{{ topicHistory.word_count }}</view>
                        <view class="item-title">已用单词数</view>
                    </view>
                </view>
            </template>
            <view v-if="topicHistory" class="completion-suggestion-box">
                {{ topicHistory.suggestion }}
            </view>
            <!-- 聊天内容 -->
            <view v-if="messageSession" class="chat-container">
                <template v-for="(message, index) in messages" :key="message.id">
                    <view class="message-content-item">
                        <message-content :auto-hint="false" :auto-play="false" :auto-pronunciation="false"
                            :message="message" :message-session="messageSession" ref="messageListRef"></message-content>
                    </view>
                </template>
            </view>
            <!-- <view class="chat-bottom-container">
                <view @click="handleDownlodImage">
                    下载聊天记录
                </view>
                <view @click="handleInitVoice">
                    语音合成下载
                </view>
            </view> -->
        </view>
    </view>
</template>
<script setup lang="ts">
import CommonHeader from "@/components/CommonHeader.vue";
import LoadingRound from "@/components/LoadingRound.vue";
import topicRequest from "@/api/topic";
import chatRequest from "@/api/chat";
import MessageContent from "@/pages/chat/components/MessageContent.vue";
import { ref } from "vue";

import { onLoad } from "@dcloudio/uni-app";

import type { Message, MessagePage, MessageSession, MessageSettings } from "@/models/chat";

const loading = ref(false);
const messageLoading = ref(false);
const topicHistory = ref(null);
const redirectType = ref(null);
const messageSession = ref<MessageSession>({
    id: undefined,
    speech_role_name: "",
    avatar: "",
    messages: { total: 0, list: [] } as MessagePage,
    topic_id: "",
});
const messages = ref<Message[]>([]);


onLoad((props) => {
    uni.setNavigationBarTitle({
		title: 'Talkie'
	});
    if (props.redirectType) {
        redirectType.value = props.redirectType;
    }
    initData(props.topicId, props.sessionId);
});

const initData = (topicId: string, sessionId: string) => {
    loading.value = true;
    // 加载历史评分
    topicRequest.getTopicCompletation({ topic_id: topicId, session_id: sessionId }).then((res) => {
        loading.value = false;
        topicHistory.value = res.data;
    });
    // 加载历史聊天记录
    messageLoading.value = true;
    chatRequest.sessionDetailsGet({ sessionId: sessionId }).then((res) => {
        messageLoading.value = false;
        messageSession.value = res.data;
        messageSession.value.messages.list.forEach((item) => {
            messages.value.push({
                id: item.id,
                session_id: item.session_id,
                content: item.content,
                role: item.role,
                owner: item.role === "USER",
                file_name: item.file_name,
                auto_hint: false,
                auto_play: false,
                auto_pronunciation: false,
                pronunciation: item.pronunciation
            });
        });
    });

};

const handleDownlodImage = () => {
    //  开发中
    uni.showToast({
        title: "开发中",
        icon: "none",
    });
};
const handleInitVoice = () => {
    //  开发中
    uni.showToast({
        title: "开发中",
        icon: "none",
    });
};
const handleBackFn = () => {
    if (redirectType.value === "index") {
        uni.switchTab({
            url: "/pages/index/index",
        });
    } else {
        uni.navigateBack();
    }
};
</script>
<style scoped lang="less">
@import url("@/less/global.less");

.content {
    margin: 30rpx 30rpx 0 30rpx;

    .completion-title-box {
        width: 100;
        padding: 32rpx 0;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;

        .completion-icon {
            width: 220rpx;
            height: 220rpx;
        }

        .completion-title {
            margin-top: 30rpx;
            height: 67rpx;
            font-size: 48rpx;
            font-weight: 400;
            color: #49CEB0;
            line-height: 67rpx;
            letter-spacing: 1px;
        }
    }

    .completion-container {
        padding: 0 50rpx;
        margin-top: 16rpx;
        display: flex;
        justify-content: space-between;

        .complete-item {
            padding: 24rpx 0;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;

            .item-data {
                height: 90rpx;
                font-size: 64rpx;
                font-weight: 600;
                color: #49CEB0;
                line-height: 90rpx;
            }

            .item-title {
                height: 40rpx;
                font-size: 28rpx;
                font-weight: 400;
                color: #707070;
                line-height: 40rpx;
            }
        }
    }
    .message-content-item {
        margin-top: 30rpx;
    }

    .completion-suggestion-box {
        margin-top: 48rpx;
        font-size: 28rpx;
        font-weight: 400;
        color: #000000;
        line-height: 50rpx;
        text-indent: 2em;
    }

    .chat-container {
        margin-top: 48rpx;
        padding-bottom: 350rpx;
    }

    .chat-bottom-container {
        background-color: #fff;
        box-sizing: border-box;
        width: 100%;
        position: fixed;
        margin: 0 auto;
        bottom: 0;
        padding-bottom: calc(env(safe-area-inset-bottom) / 2);
        display: flex;
        justify-content: space-around;
    }
}
</style>