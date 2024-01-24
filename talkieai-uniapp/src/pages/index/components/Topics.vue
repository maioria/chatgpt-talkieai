<template>
    <view class="topic-container">
        <view class="home-data">
            <view class="tab-box">
                <view :class="`tab ${activeType === 'ROLE_PLAY' ? 'tab-actice' : ''}`" @click="selectType('ROLE_PLAY')">角色扮演
                </view>
                <!-- <view :class="`tab ${activeType === 'CHAT_TOPIC' ? 'tab-actice' : ''}`" @click="selectType('CHAT_TOPIC')">
                    话题畅聊
                </view>
                <view :class="`tab ${activeType === 'TOOLS' ? 'tab-actice' : ''}`" @click="selectType('TOOLS')">
                    学习工具
                </view> -->
            </view>

            <view class="type-box">

                <LoadingRound v-if="loading" />

                <view v-if="activeType == 'CHAT_TOPIC'" class="free-topic-box" @click="goAccountCreatePage">
                    <view class="free-topic-title">
                        自由畅聊
                    </view>
                    <view class="free-topic-description">
                        写下你想要的场景，让你的角色扮演更加自由
                    </view>
                </view>

                <view class="group-box">
                    <view v-for="group in topicData" :key="group.id"
                        :class="`group-item ${activeGroup == group.id ? 'active' : ''}`" @click="handleActiveGroup(group)">
                        <view class="group-title">{{ group.name }}</view>
                    </view>
                </view>

                <view class="topic-box">
                    <view v-for="topic in topics" :key="topic.id" class="topic-item" @click="goTopic(topic)">
                        <image v-if="topic.image_url" class="topic-image" :src="topic.image_url" mode="aspectFill" />

                        <view class="topic-title">{{ topic.name }}</view>

                        <!-- 根据level属性来生成对应星星数量 -->
                        <view class="level-box">
                            <image class="level-icon" v-for="index in topic.level"
                                :key="'level_icon_' + topic.id + '_' + index" src="/static/img/icons/star.png" />
                        </view>
                        <!-- 用户是否已经完成此次话题 -->
                        <view class="completed-box" v-if="topic.completed === '1'">
                            <view class="completed-text">
                                已学习
                            </view>
                        </view>
                    </view>
                </view>
            </view>
        </view>
    </view>
</template>
<script setup lang="ts">
import LoadingRound from "@/components/LoadingRound.vue";
import topicRequest from "@/api/topic";

import { onMounted, ref } from "vue";

const loading = ref(false);
const topicData = ref(null);
const activeType = ref('ROLE_PLAY');
const activeGroup = ref(null);
const topics = ref([]);

onMounted(() => {
    uni.setNavigationBarTitle({
        title: "Talkie",
    });
    selectType('ROLE_PLAY');
});

const selectType = (type: string) => {
    activeType.value = type;
    loading.value = true;
    topics.value = [];
    topicRequest.getTopicData({ type }).then((res) => {
        loading.value = false;
        topicData.value = res.data
        if (res.data && res.data.length > 0) {
            handleActiveGroup(res.data[0]);
        } else {
            handleActiveGroup(null);
        }
    });
};

const handleActiveGroup = (group: any | null) => {
    if (group) {
        activeGroup.value = group.id;
        topics.value = group.topics;
    } else {
        activeGroup.value = null;
        topics.value = [];
    }
};

const goTopic = (topic: any) => {
    uni.navigateTo({
        url: `/pages/topic/index?topicId=${topic.id}`,
    });
};

const goAccountCreatePage = () => {
    uni.navigateTo({
        url: `/pages/topic/topicCreate`,
    });
};
</script>
<style lang="scss" scoped>
.topic-container {
    .tab-box {
        display: flex;
        padding: 32rpx 0;
        align-items: center;

        .tab {
            margin-right: 44rpx;
            font-size: 36rpx;
            position: relative;
            display: flex;
            justify-content: center;
            transition: 0.1s all linear;
            height: 50rpx;
            line-height: 50rpx;
        }

        .tab-actice {
            font-size: 42rpx;
            font-weight: 500;
        }

        .tab-actice::after {
            position: absolute;
            content: "";
            background: #6236ff;
            width: 100rpx;
            height: 10rpx;
            border-radius: 5rpx;
            bottom: -20rpx;
        }
    }

    .type-box {
        .free-topic-box {
            background-color: #f1f1f3;
            border-radius: 32rpx;
            padding: 32rpx;
            margin-top: 28rpx;

            .free-topic-title {
                font-size: 36rpx;
                font-weight: 500;
            }

            .free-topic-description {
                font-size: 28rpx;
                color: #999;
                margin-top: 16rpx;
            }
        }

        .group-box {
            margin-top: 32rpx;
            display: flex;
            flex-direction: row;
            gap: 18rpx;

            .group-item {
                width: 156rpx;
                height: 60rpx;
                border-radius: 10rpx;
                background: #F1F1F3;
                display: flex;
                align-items: center;
                justify-content: center;

                &.active {
                    color: #fff;
                    background: rgba(84, 86, 235, 0.1);
                    border: 2rpx solid #6236FF;

                    .group-title {
                        color: #6236FF;
                    }
                }

                .group-title {
                    width: 116rpx;
                    font-size: 28rpx;
                    font-weight: 400;
                    color: #5E5E5E;
                }
            }
        }

        .topic-box {
            display: flex;
            flex-wrap: wrap;
            margin-top: 54rpx;
            gap: 40rpx;

            .topic-item {
                position: relative;

                .topic-image {
                    background-color: #f1f1f3;
                    width: 323rpx;
                    height: 323rpx;
                    border-radius: 20rpx;
                    background: #FFFFFF;
                    box-shadow: 0rpx 0rpx 8rpx 0rpx rgba(160, 160, 160, 0.5);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    position: relative;
                }

                .topic-title {
                    margin-top: 20rpx;
                    width: 100%;
                    text-align: center;
                    color: #000;
                    font-size: 36rpx;
                }

                .level-box {
                    position: absolute;
                    padding: 10rpx;
                    top: 0;
                    right: 0;
                    background: rgba(255, 255, 255, 0.5);
                    border-radius: 0rpx 21rpx 0rpx 20rpx;

                    .level-icon {
                        width: 32rpx;
                        height: 32rpx;
                    }
                }

                .completed-box {
                    position: absolute;
                    bottom: 86rpx;
                    right: 16rpx;
                    background: #F1F1F3;
                    padding: 5rpx 10rpx;
                    border-radius: 10rpx;

                    .completed-text {
                        color: #5E5E5E;
                        font-size: 24rpx;
                    }
                }
            }
        }
    }
}
</style>