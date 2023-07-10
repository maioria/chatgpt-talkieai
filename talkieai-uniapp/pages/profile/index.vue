<template>
	<view class="container">
		<cu-custom bgColor="bg-gradual-blue" :isBack="true" :backFn="handleBackToEntrance">
			<block slot="content">
				个人中心
			</block>
		</cu-custom>
		<view class="cu-card dynamic no-card">
			<view class="cu-item shadow">
				<view class="cu-list menu-avatar padding-lg">
					<view class="flex">
						<image v-if="accountInfo.avatar_url" class="cu-avatar round lg" mode="aspectFill"
							:src="accountInfo.avatar_url">
						</image>
						<image v-else class="cu-avatar round lg" mode="aspectFill"
							:src="globalData.defaultAccountAvatar">
						</image>
						<view class="content margin-left-lg padding-tb-xs">
							<view class="text-xl">{{accountInfo.nick_name || accountInfo.id}}</view>
							<view class="text-gray text-xl margin-top-sm">
								{{accountInfo.mobile || ''}}
							</view>
						</view>
					</view>
				</view>
			</view>
		</view>
		<view class="cu-card dynamic no-card margin-top-sm">
			<view class="cu-list menu sm-border">
				<template v-if="accountInfoUsage.day_system_count">
					<view class="cu-item padding-top-xs">
						<view class="content">
							<text class="cuIcon-circlefill text-grey"></text>
							<text class="text-grey">
								聊天: {{accountInfoUsage.system_count}} / {{accountInfoUsage.day_system_count}}
							</text>
						</view>
					</view>
					<view class="cu-item padding-top-xs">
						<view class="content">
							<text class="cuIcon-circlefill text-grey"></text>
							<text class="text-grey">
								录音: {{accountInfoUsage.speech_count}} / {{accountInfoUsage.day_speech_count}}
							</text>
						</view>
					</view>
					<view class="cu-item padding-top-xs">
						<view class="content">
							<text class="cuIcon-circlefill text-grey"></text>
							<text class="text-grey">
								语音转换: {{accountInfoUsage.transform_count}} / {{accountInfoUsage.day_transform_count}}
							</text>
						</view>
					</view>
					<view class="cu-item padding-top-xs">
						<view class="content">
							<text class="cuIcon-circlefill text-grey"></text>
							<text class="text-grey">
								提示: {{accountInfoUsage.prompt_count}} / {{accountInfoUsage.day_prompt_count}}
							</text>
						</view>
					</view>
				</template>
			</view>
		</view>
	</view>
</template>

<script>
	import api from '@/utils/api';
	import __config from '@/config/env';
	const app = getApp();
	export default {
		data() {
			return {
				globalData: app.globalData,
				accountInfo: {},
				accountInfoUsage: {}
			}
		},
		mounted() {
			let self = this;
			api.getUserInfo().then(data => {
				this.accountInfo = data.data;
			});
		},
		onShow() {
			let self = this;
			api.getUserInfo().then(data => {
				this.accountInfo = data.data;
			});
			api.getUserInfoUsage().then(data => {
				this.accountInfoUsage = data.data;
			});
		},
		methods: {
			handleBackToEntrance() {
				uni.redirectTo({
					url: '/pages/index/entrance'
				})
			}
		}
	}
</script>