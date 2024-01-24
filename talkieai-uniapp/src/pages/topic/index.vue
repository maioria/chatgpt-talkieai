<template>
    <view class="container">
        <CommonHeader :leftIcon="true" :back-fn="handleBackPage" backgroundColor="#F5F5FE">
            <template v-slot:content>
                <text></text>
            </template>
        </CommonHeader>
        <view class="content">
            <LoadingRound v-if="loading" />
            <view v-if="topicDetail" class="topic-content">
                <view class="profile-box">
                    <image class="profile-image" :src="topicDetail.image_url" mode="aspectFill" />
                    <view class="name-box">
                        {{ topicDetail.name }}
                        <image @click="goTopicHistory" class="icon" src="/static/img/icons/history-records.png" />
                    </view>
                </view>

                <view class="description-box">
                    <view class="description-title">
                        场景
                    </view>
                    <view class="description-content">
                        {{ topicDetail.description }}
                    </view>
                </view>

                <!-- 目标 -->
                <view class="main-target-box">
                    <view class="main-target-title">
                        目标
                    </view>
                    <view class="main-target-content">
                        <view v-for="main_target in topicDetail.main_targets" :key="main_target.id"
                            class="main-target-item">
                            {{ main_target.description }}
                        </view>
                    </view>
                </view>

                <!-- 也试试 -->
                <view v-if="topicDetail.trial_targets && topicDetail.trial_targets.length > 0" class="main-target-box">
                    <view class="main-target-title">
                        也试试
                    </view>
                    <view class="main-target-content">
                        <view v-for="main_target in topicDetail.trial_targets" :key="main_target.id"
                            class="main-target-item">
                            {{ main_target.description }}
                        </view>
                    </view>
                </view>
            </view>
        </view>

        <!-- 底部操作栏 -->
        <view class="bottom-box">
            <view class="atk-btn-box gray" @click="goTopicPurchase">
                <text class="atk-btn">查看短语手册</text>
            </view>
            <view class="atk-btn-box start-btn-box" @click="goChat">
                <text class="atk-btn">开始</text>
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

const loading = ref(false);
const topicDetail = ref(null);


onLoad((props) => {
    uni.setNavigationBarTitle({
		title: 'Talkie'
	});

    getTopicDetail(props.topicId);

});

const getTopicDetail = (topicId: string) => {
    loading.value = true;
    topicRequest.getTopicDetail(topicId).then((res) => {
        loading.value = false;
        topicDetail.value = res.data;
    });
};

const goTopicHistory = () => {
    uni.navigateTo({
        url: `/pages/topic/history?topicId=${topicDetail.value.id}`
    });
};

const goTopicPurchase = () => {
    uni.navigateTo({
        url: `/pages/topic/phrase?topicId=${topicDetail.value.id}`
    });
};

/**
 * 先生成session信息，再根据session进行跳转
 */
const goChat = () => {
    topicRequest.createSession({ topic_id: topicDetail.value.id }).then((res) => {
        console.log(res.data.id)
        uni.navigateTo({
            url: `/pages/chat/index?sessionId=${res.data.id}`
        });
    });
};

const handleBackPage = () => {
    uni.switchTab({
        url: '/pages/index/index'
    });
};

</script>
<style scoped lang="less">
@import url("@/less/global.less");

.container {
    background-color: #F5F5FE;
}

.content {
    margin: 0 32rpx;
    padding-bottom: 330rpx;

    .topic-content {
        .profile-box {
            display: flex;
            flex-direction: column;
            align-items: center;

            .profile-image {
                width: 320rpx;
                height: 320rpx;
                border-radius: 30rpx;
            }

            .name-box {
                font-size: 36rpx;
                font-weight: bold;
                margin-top: 32rpx;
            }
        }

        .description-box {
            margin-top: 32rpx;

            .description-title {
                font-size: 36rpx;
                color: #333;
            }

            .description-content {
                margin-top: 16rpx;
                font-size: 28rpx;
                color: #666;
            }
        }

        .main-target-box {
            margin-top: 64rpx;

            .main-target-title {
                font-size: 36rpx;
                color: #333;
            }

            .main-target-content {
                margin-top: 16rpx;
                padding: 16rpx 32rpx;
                font-size: 28rpx;
                color: #666;
                background-color: #fff;
                border-radius: 24rpx;

                .main-target-item {
                    // padding: 16rpx 32rpx;
                    border-bottom: 1px solid #f1f1f3;
                    line-height: 80rpx;
                    height: 80rpx;
                }
            }
        }
    }
}

.bottom-box {
    background-color: #F5F5FE;

    .start-btn-box {
        margin-top: 24rpx;
    }
}
</style>