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
					<image class="profile-avatar" src="/static/default-avatar.png" />
					<text class="profile-name">请登录</text>
				</view>
				<view v-else class="profile">
					<image class="profile-avatar" src="/static/default-avatar.png" />
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
				<view v-if="accountInfo.account_id.indexOf('visitor') < 0" class="setting-card" @tap="hangleLogout">
					<image class="setting-card-logo" src="/static/feedback.png" />
					<text class="setting-card-title">退出登录</text>
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


const accountInfo = ref<AccountInfo>({ account_id: '', today_chat_count: 0, total_chat_count: 0 });

onMounted(() => {
	accountRequest.accountInfoGet().then((data) => {
		accountInfo.value = data.data;
	});
	uni.setNavigationBarTitle({
		title: 'TalkieAI'
	});
});

const goSetting = () => {
	uni.navigateTo({
		url: '/pages/setting/index'
	})
}
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
</script>
<style scoped src="./less/index.less" lang="less"></style>
