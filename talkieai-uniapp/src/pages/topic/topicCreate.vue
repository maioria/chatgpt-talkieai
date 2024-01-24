<template>
    <view class="container">
        <CommonHeader :leftIcon="true" backgroundColor="#F5F5FE">
            <template v-slot:content>
                <text></text>
            </template>
        </CommonHeader>
        <view class="content">
            <view class="create-topic-container">
                <view class="title">
                    您想谈些什么？
                </view>
                <view class="random-btn-box">
                    <view @click="handleRandomTopic" class="random-btn">
                        随机话题
                    </view>
                </view>
                <view class="input-box">
                    <view class="input-item">
                        <view class="item-title">
                            我的角色
                        </view>
                        <input class="item-input" :placeholder="randomInput.my_role" />
                    </view>
                </view>
                <view class="input-box">
                    <view class="input-item">
                        <view class="item-title">
                            AI的角色
                        </view>
                        <input class="item-input" :placeholder="randomInput.ai_role" />
                    </view>
                </view>
                <view class="input-box">
                    <view class="input-item">
                        <view class="item-title">
                            情境
                        </view>
                        <input class="item-input" :placeholder="randomInput.topic" />
                    </view>
                </view>
                <view class="btn-box">
                    <view class="btn" @click="createTopic">
                        创建话题
                    </view>
                </view>
            </view>
            <view class="my-topic-container">

            </view>
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

interface TopicModel {
    id: string;
    my_role: string;
    ai_role: string;
    topic: string;
}

interface CreateModel {
    my_role: string;
    ai_role: string;
    topic: string;
}

const randomInput = ref<CreateModel>({
    my_role: "",
    ai_role: "",
    topic: "",
});

const myTopics = ref<TopicModel[]>([]);

onLoad(() => {
    uni.setNavigationBarTitle({
		title: 'Talkie'
	});
    initMyTopics();
});

const initMyTopics = () => {
    topicRequest.getMyTopics().then((res) => {
        console.log(res.data);
    });
};

const handleRandomTopic = () => {
    topicRequest.getTopicExample().then((res) => {
        randomInput.value = res.data;
    });
};

const createTopic = () => {
    const { my_role, ai_role, topic } = randomInput.value;
    if (!my_role || !ai_role || !topic) {
        uni.showToast({
            title: "请填写完整",
            icon: "none",
        });
        return;
    }
    topicRequest.createTopic({ my_role, ai_role, topic }).then((res) => {
        const account_topic_id = res.data
        uni.navigateTo({
            url: `/pages/chat/index?accountTopicId=account_topic_id`,
        });
    });
};
</script>
<style lang="scss" scoped>
.container {
    .content {
        margin-top: 48rpx;
        padding: 0 32rpx;

        .title {
            font-size: 40rpx;
            font-weight: 400;
            color: #333333;
            text-align: center;
        }

        .random-btn-box {
            margin-top: 48rpx;
            display: flex;
            justify-content: flex-end;

            .random-btn {
                color: #333333;
                font-size: 32rpx;
            }
        }

        .input-box {
            .input-item {
                margin-top: 16rpx;

                .item-title {
                    font-size: 32rpx;
                }

                .item-input {
                    padding: 16rpx;
                    border-radius: 8rpx;
                    border-bottom: 1px solid #E5E5E5;
                    font-size: 32rpx;
                    color: #333333;
                }
            }
        }

        .btn-box {
            margin-top: 48rpx;
            display: flex;
            justify-content: center;

            .btn {
                width: 600rpx;
                height: 100rpx;
                background-color: #6236FF;
                border-radius: 50rpx;
                color: #fff;
                font-size: 32rpx;
                display: flex;
                justify-content: center;
                align-items: center;
            }
        }
    }
}
</style>