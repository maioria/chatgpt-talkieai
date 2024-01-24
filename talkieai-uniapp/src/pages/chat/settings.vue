<template>
    <view>
        <CommonHeader :leftIcon="true" :back-fn="handleBackPage" title="Talkie">
            <template v-slot:content>
                <text>设置</text>
            </template>
        </CommonHeader>
        <view class="mine-content">
            <view class="setting">
                <view class="setting-card">
                    <text class="setting-card-title">AI角色</text>
                    <text @click="goSwitchRole">{{ settingInfo.speech_role_name_label || '默认角色' }}</text>
                </view>
                <view class="setting-card">
                    <text class="setting-card-title">自动播放语音</text>
                    <Checkbox @input="(check) => inputCheck('auto_playing_voice', check)"
                        :checked="settingInfo.auto_playing_voice === 1" />
                </view>
                <view class="setting-card">
                    <text class="setting-card-title">自动模糊文本</text>
                    <Checkbox @input="(check) => inputCheck('auto_text_shadow', check)"
                        :checked="settingInfo.auto_text_shadow === 1" />
                </view>
                <view class="setting-card">
                    <text class="setting-card-title">自动语音评分</text>
                    <Checkbox @input="(check) => inputCheck('auto_pronunciation', check)"
                        :checked="settingInfo.auto_pronunciation === 1" />
                </view>
            </view>
            <view class="setting-bot">
                <text class="setting-card-title">语速</text>
                <view class="tab-box">
                    <view :class="`tab-item ${settingInfo.playing_voice_speed == '0.5' ? 'tab-item-select' : ''}`" @tap="selectTab('0.5')">
                        <text>慢速</text>
                    </view>
                    <view :class="`tab-item ${settingInfo.playing_voice_speed == '1.0' ? 'tab-item-select' : ''}`" @tap="selectTab('1.0')">
                        <text>正常</text>
                    </view>
                    <view :class="`tab-item ${settingInfo.playing_voice_speed == '1.5' ? 'tab-item-select' : ''}`" @tap="selectTab('1.5')">
                        <text>较快</text>
                    </view>
                </view>
                <button @tap="deleteLatestMessages" class="common-button setting-clear-latest">
                    清空上一次聊天记录
                </button>
                <button @tap="deleteAllMessages" class="common-button setting-clear">
                    清空所有聊天记录
                </button>
            </view>
        </view>
    </view>
</template>
  
<script setup lang="ts">
import CommonHeader from "@/components/CommonHeader.vue";
import Checkbox from "@/components/Checkbox.vue";
import { ref } from "vue";
import { onShow } from "@dcloudio/uni-app";
import { onLoad } from "@dcloudio/uni-app";
import accountRequest from "@/api/account";
import chatRequest from "@/api/chat";
const settingInfo = ref<any>({});
const sessionId = ref<string>("");
// Todo 需要在设置值变化时调用后台进行更新，设置完后chat页面能实时获取更新数据

onLoad((options: any) => {
    uni.setNavigationBarTitle({
		title: 'Talkie'
	});
    sessionId.value = options.sessionId;
});

onShow(() => {
    accountRequest.getSettings().then((data) => {
        if (data.code === "200") {
            settingInfo.value = data.data;
        }
    });
});

const goSwitchRole = () => {
    uni.navigateTo({
        url: "/pages/index/switchRole",
    });
};

/**
 * 回到主页面
 */
const handleBackPage = () => {
    uni.navigateBack({
        delta: 1,
    });
};

const selectTab = (id: string) => {
    settingInfo.value.playing_voice_speed = id;
    accountRequest.setSettings({
        'playing_voice_speed': id,
    }).then((data) => {
        console.log(data);
        if (data.code === "200") {
            console.log("设置成功");
        }
    });
};

const inputCheck = (type: string, check: boolean) => {
    accountRequest.setSettings({
        [type]: check ? 1 : 0,
    }).then((data) => {
        console.log(data);
        if (data.code === "200") {
            console.log("设置成功");
        }
    });
};

const deleteLatestMessages = () => {
    uni.showModal({
        title: "提示",
        content: "确定清空上一次聊天记录吗？",
        success: function (res) {
            if (res.confirm) {
                console.log("用户点击确定");
                chatRequest.messagesLatestDelete(sessionId.value).then((data) => {
                    console.log(data);
                    uni.showToast({
                        title: "清空成功",
                        icon: "none",
                    });
                    uni.navigateTo({
                        url: `/pages/chat/index?sessionId=${sessionId.value}`,
                    });
                });
            } else if (res.cancel) {
                console.log("用户点击取消");
            }
        },
    });
};

const deleteAllMessages = () => {
    uni.showModal({
        title: "提示",
        content: "确定清空聊天记录吗？",
        success: function (res) {
            if (res.confirm) {
                console.log("用户点击确定");
                chatRequest.messagesAllDelete(sessionId.value).then((data) => {
                    console.log(data);
                    uni.showToast({
                        title: "清空成功",
                        icon: "none",
                    });
                    uni.navigateTo({
                        url: `/pages/chat/index?sessionId=${sessionId.value}`,
                    });
                });
            } else if (res.cancel) {
                console.log("用户点击取消");
            }
        },
    });
};
</script>
<style scoped lang="less">
@import url('@/less/global.less');

.common-switch {
    .uni-switch-input {
        border-color: #5d33f9;
        background-color: #5d33f9;
    }
}

.mine-content {
    background: #fff;
    min-height: calc(100vh - 100rpx);

    .setting {
        margin-top: 38rpx;

        .setting-card {
            background: #fff;
            background-size: 16rpx 28rpx;
            border-bottom: 1px solid #e8e8e8;
            padding: 0 28rpx;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 50rpx 32rpx;

            .setting-card-logo {
                width: 28rpx;
                height: 28rpx;
                margin-right: 20rpx;
            }

            .setting-card-title {}
        }
    }

    .setting-bot {
        padding: 36rpx;
        .setting-clear-latest {
            width: 100%;
            background: #F1F1F3;
            border-radius: 30rpx;
            color: #333;
            font-size: 28rpx;
            margin-top: 150rpx;
        }

        .setting-clear {
            width: 100%;
            background: #F1F1F3;
            border-radius: 30rpx;
            color: #333;
            font-size: 28rpx;
            margin-top: 20rpx;
        }

        .setting-clear::after {
            border: none;
        }
    }

    .tab-box {
        width: 100%;
        background: #F1F1F3;
        border-radius: 30rpx;
        display: flex;
        flex: 1;
        padding: 10rpx;
        margin-top: 50rpx;

        .tab-item {
            display: block;
            flex: 1;
            text-align: center;
            padding: 34rpx 0;
            transition: .3s all linear;
        }

        .tab-item:active {
            opacity: .9;
        }

        .tab-item-select {
            background: #fff;
            color: #333;
            border-radius: 30rpx;
        }
    }
}
</style>
  