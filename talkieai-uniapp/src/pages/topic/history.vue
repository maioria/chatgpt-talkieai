<template>
    <view class="container">
        <CommonHeader :leftIcon="true" :back-fn="handleBackPage" backgroundColor="#F5F5FE">
            <template v-slot:content>
                <text>课程历史记录</text>
            </template>
        </CommonHeader>
        <view class="content">
            <view class="history-list">
                <template v-if="historyArray.length > 0">
                    <view v-for="history in historyArray" class="history-item">
                        <view class="history-content">
                            <view class="image-box" @click="goDetail(history)">
                                <image class="topic-image" :src="history.topic.image_url" mode="aspectFill" />
                            </view>
                            <view class="intro-box" @click="goDetail(history)">
                                <view class="topic-name">
                                    {{ history.topic.topic }}
                                </view>
                                <view class="topic-time">
                                    {{ history.create_time }}
                                </view>
                                <view class="completed-box">
                                    <view class="completed-text-box" :class="{ 'active': history.completed === '1' }">
                                        <view v-if="history.completed === '1'" class="completed-text">
                                            已完成
                                        </view>
                                        <view v-else class="completed-text">
                                            未完成
                                        </view>
                                    </view>
                                    <view class="completed-text-space"></view>
                                </view>
                            </view>
                            <view @click="handleDelete(history)" class="delete-btn-box">
                                <image class="delete-btn" src="/static/deleted.png" mode="heightFix" />
                            </view>
                        </view>
                        <view class="line"></view>
                    </view>
                </template>
                <view v-else>
                    暂时没有任何历史记录
                </view>
            </view>
        </view>
    </view>
</template>

<script setup lang="ts">
import CommonHeader from "@/components/CommonHeader.vue";
import LoadingRound from "@/components/LoadingRound.vue";
import topicRequest from "@/api/topic";
import { ref } from "vue";

import { onLoad } from "@dcloudio/uni-app";

const topicId = ref('');
const loading = ref(false);
const historyArray = ref([]);

onLoad((props) => {
    uni.setNavigationBarTitle({
		title: 'Talkie'
	});
    topicId.value = props.topicId;
    initData(props.topicId);
});

const initData = (topicId: string) => {
    loading.value = true;
    topicRequest.getTopicHistory(topicId).then((data) => {
        loading.value = false;
        historyArray.value = data.data;
    });
};

const handleBackPage = () => {
    uni.navigateTo({
        url: `/pages/topic/index?topicId=${topicId.value}`
    });
};

const goDetail = (history) => {
    // 如果 completed为1 跳转到完成页面，否则跳转到聊天详情
    if (history.completed == 1) {
        uni.navigateTo({
            url: `/pages/topic/completion?topicId=${topicId.value}&sessionId=${history.session_id}`
        });
    } else {
        uni.navigateTo({
            url: `/pages/chat/index?sessionId=${history.session_id}&backPage=topic&topicId=${topicId.value}`
        });
    }
};

const handleDelete = (history) => {
    uni.showModal({
        title: "提示",
        content: "是否删除该历史记录",
        confirmColor: "#6236ff",
        success: (res) => {
            if (res.confirm) {
                // 用户点击确定
                const params = {
                    topic_id: history.topic_id,
                    session_id: history.session_id
                };
                topicRequest.deleteTopicHistory(params).then(() => {
                    uni.showToast({
                        title: "删除成功",
                        icon: "none",
                    });
                    initData(topicId.value);
                });
            } else if (res.cancel) {
                // 用户点击取消
            }
        },
    });
};
</script>

<style scoped lang="less">
@import url("@/less/global.less");

.container {
    min-height: 100vh;

    .content {
        padding: 32rpx 0;

        .history-item {
            margin-top: 6rpx;

            .history-content {
                padding: 0 32rpx;
                background-color: #fff;
                display: flex;

                .image-box {
                    .topic-image {
                        width: 140rpx;
                        height: 140rpx;
                        background: #FFFFFF;
                        box-shadow: 0rpx 0rpx 8rpx 0rpx rgba(160, 160, 160, 0.5);
                        border-radius: 20rpx;
                    }
                }

                .intro-box {
                    margin-left: 30rpx;
                    flex: 1;

                    .topic-name {
                        font-size: 28rpx;
                        font-weight: 500;
                    }

                    .topic-time {
                        margin-top: 10rpx;
                        font-size: 28rpx;
                        color: #707070;
                    }

                    .completed-box {
                        margin-top: 12rpx;
                        display: flex;

                        .completed-text-box {
                            padding: 5rpx 10rpx;
                            background: #F1F1F3;
                            border-radius: 10rpx;
                            color: #5E5E5E;
                            font-size: 24rpx;

                            &.active {
                                background: rgba(84, 86, 235, 0.1);
                                border: 2rpx solid #6236FF;
                                color: #6236FF;
                            }
                        }

                        .completed-text-space {
                            flex: 1;
                        }
                    }
                }

                .delete-btn-box {
                    .delete-btn {
                        width: 32rpx;
                        height: 32rpx;
                    }
                }
            }

            .line {
                margin: 38rpx 0;
                height: 1rpx;
                border: 1rpx solid #E8E8E8;
            }


        }
    }
}
</style>