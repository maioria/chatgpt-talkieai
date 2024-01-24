<template>
	<view class="my-container">
		<CommonHeader class="header" title="Talkie">
			<template v-slot:content>
				<text>个人中心</text>
			</template>
		</CommonHeader>
		<view class="mine-content">
			<!-- profile -->
			<view class="profile-box">
				<view v-if="accountInfo.account_id.indexOf('visitor') === 0" class="profile" @tap="hangleLogin">
					<image class="profile-avatar" src="/static/default-account-avatar.png" />
					<text class="profile-name">请登录</text>
				</view>
				<view v-else class="profile">
					<image class="profile-avatar" src="/static/default-account-avatar.png" />
					<text class="profile-name">{{ accountInfo.account_id }}</text>
				</view>
			</view>
			<view class="mine-message-box">
				<view class="mine-list-box">
					<view class="mine-list-item">
						<text class="mine-list-item-title">今日次数</text>
						<view><text class="mine-list-item-num">{{ accountInfo.today_chat_count }}</text></view>
					</view>
					<view class="mine-list-item">
						<text class="mine-list-item-title mine-list-item-title-total">总次数</text>
						<view><text class="mine-list-item-num">{{ accountInfo.total_chat_count }}</text></view>
					</view>
				</view>
			</view>
			<view class="setting">
				<!-- <view class="setting-card" @tap="goSetting">
					<image class="setting-card-logo" src="/static/setting.png" />
					<text class="setting-card-title">设置</text>
				</view> -->
				<view class="setting-card" @tap="goLearningLanguage">
					<image class="setting-card-logo" src="/static/setting.png" />
					<text class="setting-card-title">学习语言</text>
					<text class="setting-card-value" style="margin-right: 50rpx;">{{ accountInfo.target_language_label }}</text>
				</view>
				<view class="setting-card" @tap="goFeedback">
					<image class="setting-card-logo" src="/static/feedback.png" />
					<text class="setting-card-title">反馈</text>
				</view>
				<view class="setting-card" @tap="goContact">
					<image class="setting-card-logo" src="/static/concat.png" />
					<text class="setting-card-title">联系我们</text>
				</view>
				<view class="setting-card" @tap="goGithub">
					<image class="setting-card-logo" src="/static/github/github-mark.png" />
					<text class="setting-card-title">Github</text>
				</view>
				<!-- 如果是小程序登录 -->
				<view v-if="accountInfo.account_id.indexOf('visitor') < 0" class="logout-box" @tap="hangleLogout">
					<!-- <image class="setting-card-logo" src="/static/default-account-avatar.png" /> -->
					<text class="setting-card-title logout-text">退出登录</text>
				</view>
			</view>
		</view>
	</view>
</template>

<script setup lang="ts">
import CommonHeader from "@/components/CommonHeader.vue";
import { ref, reactive, onMounted } from "vue";

import accountRequest from '@/api/account';
import type { AccountInfo } from '@/models/models';
import {  onShow } from "@dcloudio/uni-app";


const accountInfo = ref<AccountInfo>({ account_id: '', today_chat_count: 0, total_chat_count: 0, target_language_label: '' });

onMounted(() => {
	uni.setNavigationBarTitle({
		title: 'TalkieAI'
	});
});

onShow(() => {
	accountRequest.accountInfoGet().then((data) => {
		accountInfo.value = data.data;
	});
});

const goContact = () => {
	uni.navigateTo({
		url: '/pages/contact/index'
	})
}

const goGithub = () => {
	const redirectUrl = 'https://github.com/maioria/chatgpt-talkieai/issues';
	// #ifdef H5
	window.open(redirectUrl);
	// #endif

	// 非h5的情况提示用户访问 chatgpt-talkieai
	// #ifndef H5
	uni.showToast({
		title: '可通过github访问 chatgpt-talkieai',
		icon: 'none'
	})
	// #endif
}

const hangleLogout = () => {
	uni.showModal({
		title: '提示',
		content: '确定退出登录吗？',
		confirmColor: '#6236ff',
		success: function (res) {
			if (res.confirm) {
				uni.removeStorageSync('x-token');
				uni.reLaunch({
					url: '/pages/login/index'
				})
			} else if (res.cancel) {
				console.log('用户点击取消');
			}
		}
	});
}

const hangleLogin = () => {
	uni.removeStorageSync('x-token');
	uni.reLaunch({
		url: '/pages/login/index'
	})
}

const goFeedback = () => {
	uni.navigateTo({
		url: '/pages/feedback/index'
	})
}

const goLearningLanguage = () => {
	uni.navigateTo({
		url: '/pages/my/learnLanguage'
	});
}
</script>
<style scoped lang="less">
@import url('@/less/global.less');

.my-container {
	background: linear-gradient(180deg, #F5F5FE 0%, #FFFFFF 100%);
}

.mine-content {
	padding-bottom: 48rpx;

	.profile-box {
		height: 176rpx;
		background: #FFFFFF;
		box-shadow: 0rpx 0rpx 8rpx 0rpx rgba(196, 196, 196, 0.5);
		border-radius: 30rpx;
		padding: 28rpx;
		margin: 32rpx;

		.profile {
			display: flex;
			align-items: center;

			.profile-avatar {
				width: 120rpx;
				height: 120rpx;
				border-radius: 60rpx;
			}

			.profile-name {
				margin-left: 40rpx;
				height: 40rpx;
				font-size: 28rpx;
				font-weight: 500;
				color: #000000;
				line-height: 40rpx;
			}
		}

	}

	.setting {
		margin-top: 38rpx;

		.setting-card {
			height: 100rpx;
			background: url('@/static/right.png') no-repeat 706rpx center #fff;
			background-size: 16rpx 28rpx;
			padding: 0 28rpx;
			display: flex;
			align-items: center;

			.setting-card-logo {
				width: 28rpx;
				height: 28rpx;
				margin-right: 20rpx;
			}

			.setting-card-title {
				flex: 1;
			}
		}

		.setting-card:active {
			background-color: #ddd;
		}
	}

	.mine-message-box {
		padding: 60rpx 60rpx 0;

		.logo {
			width: 100%;
			height: 240rpx;
		}

		.mine-list-box {
			display: flex;
			padding-bottom: 40rpx;

			.mine-list-item {
				background: #fff;
				height: 220rpx;
				border-radius: 30rpx;
				width: 50%;
				padding: 38rpx;
			}

			.mine-list-item:nth-child(2n) {
				margin-left: 32rpx;
			}

			.mine-list-item-title {
				font-size: 28rpx;
				color: #000;
				padding-left: 24rpx;
				position: relative;

			}

			.mine-list-item-title::after {
				position: absolute;
				content: '';
				width: 10rpx;
				height: 28rpx;
				border-radius: 5rpx;
				left: 0;
				top: 4rpx;
				background: #6236FF;
			}

			.mine-list-item-title-total::after {
				background: #FF6B6B;
			}

			.mine-list-item-num {
				font-size: 64rpx;
				color: #000;
				font-weight: 500;
			}
		}
	}

	.subscribe-box {
		border-radius: 30rpx;
		margin: 0 32rpx;
		height: 200rpx;
		background: linear-gradient(180deg, #F6E6C5 0%, #EAC993 100%);
		box-shadow: 0rpx 0rpx 8rpx 0rpx rgba(196, 196, 196, 0.5);
		border-radius: 30rpx;
		padding: 40rpx 32rpx;

		.title-box {
			display: flex;
			align-items: center;

			.vip-icon-box {
				display: flex;
				align-items: center;

				.vip-icon {
					width: 80rpx;
					height: 53rpx;
				}

				.vip-text-icon {
					margin-left: 20rpx;
					width: 104rpx;
					height: 44rpx;
				}
			}

			.title {
				margin-left: 36rpx;
				font-size: 28rpx;
				color: #59370D;
			}
		}

		.btn-box {
			margin-top: 24rpx;
			width: 100%;
			display: flex;
			justify-content: center;

			.btn {
				width: 360rpx;
				height: 60rpx;
				background: #59370D;
				border-radius: 46rpx;
				display: flex;
				align-items: center;
				justify-content: center;

				.btn-text {
					font-weight: 400;
					color: #fff;
					line-height: 40rpx;
					height: 40rpx;
					font-size: 28rpx;
				}
			}
		}

		.vip-info-box {
			display: flex;
			align-items: baseline;
			justify-content: space-between;

			.btn-text {
				height: 40rpx;
				font-size: 28rpx;
				font-weight: 400;
				color: #000000;
				line-height: 40rpx;
			}

			.btn-box {
				padding: 10rpx 0;
				width: 138rpx;
				background: #59370D;
				border-radius: 58rpx;
				color: #fff;
				display: flex;
				justify-items: center;
				align-items: center;
			}
		}

		.left-box {
			flex: 1;

			.subscribe-title {
				font-size: 36rpx;
			}

			.subscribe-sub-title {
				margin-top: 12rpx;
				font-size: 24rpx;
			}
		}

		.right-box {
			width: 80rpx;
		}
	}
}

.logout-box {
	display: flex;
	justify-content: center;
	align-items: center;
	background: #fff;
	height: 100rpx;
	padding: 0 28rpx;
}

.logout-text {
	color: #707070;
}
</style>
