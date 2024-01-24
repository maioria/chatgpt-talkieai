<template>
    <view class="container">
        <CommonHeader :left-icon="true" style="background-color: none; color: #fff" :back-fn="handleBackPage" title="聊天">
            <template v-slot:left>
                <image @tap="handleBackPage" class="back-icon" src="/static/icon_home.png"></image>
            </template>
            <template v-slot:content>
                <view>选择角色</view>
            </template>
        </CommonHeader>
        <view class="content">
            <swiper class="swiper" circular :indicator-dots="true" :autoplay="false" :interval="interval"
                :duration="duration" @change="swiperChange" :current="swiperCurrent">
                <swiper-item v-for="m in roles" :key="m.id" class="index-page-card-box">
                    <view class="index-page-card">
                        <view class="index-name">
                            <text class="index-name-text">{{ m.local_name }}</text>
                        </view>
                        <view class="index-header-box">
                            <image v-if="m.avatar" :src="m.avatar" class="index-header-img" />
                            <image v-else-if="m.gender == '2'"
                                src="http://qiniu.prejade.com/1597936949107363840/talkie/images/en-US_Guy.png"
                                class="index-header-img" />
                            <image v-else
                                src="https://qiniu.prejade.com/1597936949107363840/talkie/images/en-US_JennyNeural.png"
                                class="index-header-img" />
                        </view>
                        <view class="style-box">
                            <view v-for="style in m.styles" class="style-text-box">
                                <view class="style-text" :title="style">
                                    {{ style.label || '默认' }}
                                </view>
                                <AudioPlayer :content="audioPlayerContent" :speechRoleName="m.short_name"
                                    :speechRoleStyle="style.value" />
                            </view>
                        </view>
                    </view>
                </swiper-item>
            </swiper>
            <button @tap="confirmUpdate" class="common-button index-btn">
                确 认
            </button>
        </view>
    </view>
</template>
  
<script setup lang="ts">
import CommonHeader from "@/components/CommonHeader.vue";
import AudioPlayer from "@/components/AudioPlayer.vue";
import { ref, onMounted, computed, nextTick } from "vue";
import type { Role } from "@/models/chat";
import chatRequest from "@/api/chat";
import accountRequest from "@/api/account";
import sysRequest from "@/api/sys";
import { onLoad, onShow } from "@dcloudio/uni-app";

const roles = ref<Role[]>([]);
const duration = ref<number>(500);
const interval = ref<number>(2000);
const selectIndex = ref<number>(0);
const audioPlayerContent = ref<string>("");
const language = ref<string>("");
// 如果为init，则不能显示返回按钮
const redirectType = ref(null);
const swiperCurrent = ref<number>(0);

onLoad((options: any) => {
    uni.setNavigationBarTitle({
		title: 'Talkie'
	});
    if (options.redirectType) {
        redirectType.value = options.redirectType;
    }
});

onShow(() => {
    // 获取用户设置的语言，之后加载相应数据
    accountRequest.getSettings().then((data) => {
        language.value = data.data.target_language;
        initAudioPlayerContent();
        initRoles();
    });
});

const initAudioPlayerContent = () => {
    chatRequest
        .languageExampleGet({
            language: language.value,
        })
        .then((data) => {
            audioPlayerContent.value = data.data;
        });
};
const initRoles = () => {
    sysRequest
        .getRoles({
            locale: language.value,
        })
        .then((data) => {
            roles.value = data.data;
            // 获取用户设置的speech_role_name，如果有，则设置为当前选中的角色
            accountRequest.getSettings().then((data) => {
                let speechRoleName = data.data.speech_role_name;
                if (speechRoleName) {
                    let index = roles.value.findIndex(
                        (m) => m.short_name == speechRoleName
                    );
                    if (index > -1) {
                        selectIndex.value = index;
                    }
                }
                nextTick(() => {
                    swiperCurrent.value = selectIndex.value;
                });
            });
        });
};

const swiperChange = (info: any) => {
    selectIndex.value = info.detail.current;
};
// 创建会话
const confirmUpdate = () => {
    let role = roles.value[selectIndex.value];
    accountRequest.setSettings({
        speech_role_name: role.short_name
    }).then(data => {
        // 提示成功，回退到上一页
        uni.showToast({
            title: "切换成功",
            icon: "none",
            duration: 2000,
        });
        uni.navigateBack();
    });
};
/**
 * 回到主页面
 */
const handleBackPage = () => {
    uni.switchTab({
        url: "/pages/index/index",
    });
};
</script>
  
<style scoped lang="less">
@import url("@/less/global.less");

.back-icon {
    width: 48rpx;
    height: 48rpx;
}

.container {
    background: linear-gradient(135deg,
            rgba(78, 79, 234, 0.97) 0%,
            rgba(213, 214, 232, 0.97) 100%);
    height: 100vh;
}

.content {
    display: flex;
    flex-direction: column;
    align-items: center;

    position: relative;
    padding-top: 100rpx;

    .index-page-card-box {
        width: 100%;
    }

    .index-page-card {
        margin: 0;
        width: 100%;
        display: flex;
        align-items: center;
        padding: 80rpx 44rpx;
        flex-direction: column;
        background: linear-gradient(135deg,
                rgba(255, 255, 255, 0.1) 0%,
                rgba(255, 255, 255, 0.2) 100%);
        border-radius: 30rpx;

        .index-header-box {
            width: 380rpx;
            height: 380rpx;
            box-sizing: border-box;
            border-radius: 190rpx;
            background: rgba(95, 96, 235, 1);
            padding: 20rpx;

            .index-header-img {
                width: 340rpx;
                height: 340rpx;
                border-radius: 170rpx;
                background: #333;
            }
        }

    }

    .index-change-position-one {
        position: absolute;
        left: 0;
        top: 200rpx;
        width: 48rpx;
        height: 724rpx;
        background: linear-gradient(135deg,
                rgba(255, 255, 255, 0.1) 0%,
                rgba(255, 255, 255, 0.2) 100%);
        border-radius: 0 30rpx 30rpx 0;
    }

    .index-change-position-two {
        position: absolute;
        right: 0;
        top: 200rpx;
        width: 48rpx;
        height: 724rpx;
        background: linear-gradient(135deg,
                rgba(255, 255, 255, 0.1) 0%,
                rgba(255, 255, 255, 0.2) 100%);
        border-radius: 30rpx 0 0 30rpx;
    }

    .index-btn {
        margin-top: 32rpx;
    }

    .uni-margin-wrap {
        width: 690rpx;
        width: 100%;
    }

    .swiper {
        margin-top: 48rpx;
        width: 590rpx;
        height: 800rpx;
    }

    .swiper-item {
        display: block;
        width: 590rpx;
        height: 800rpx;
        text-align: center;
    }

    .swiper-list {
        margin-top: 40rpx;
        margin-bottom: 0;
    }

    .uni-common-mt {
        margin-top: 60rpx;
        position: relative;
    }

    .info {
        position: absolute;
        right: 20rpx;
    }

    .uni-padding-wrap {
        width: 550rpx;
        padding: 0 100rpx;
    }

    .index-name {
        display: flex;
        align-items: center;
        color: #fff;
        font-size: 30rpx;
        top: 20rpx;
        text-align: center;
        display: flex;
        justify-content: center;
        align-items: center;
        position: absolute;
    }

    .style-box {
        display: flex;
        flex-wrap: wrap;

        .style-text-box {
            display: flex;
            padding: 5rpx 12rpx;
            border: none;
            margin-left: 10rpx;
            margin-top: 10rpx;
            background: #7879d4;
            color: #adaded;
            justify-content: center;
            align-items: center;
            border-radius: 6rpx;
        }

        .style-text {
            font-size: 26rpx;
            max-width: 5rem;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }
    }
}</style>
  