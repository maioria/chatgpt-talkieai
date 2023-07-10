<script>
	import Vue from 'vue'
	import api from '@/utils/api';
	import Fingerprint2 from 'fingerprintjs2';
	const X_TOKEN = 'x-token';
	export default {
		globalData: {
			xToken: null,
			female_avatar: '',
			male_avatar: '',
			CustomBar: null,
			userInfo: {},
			defaultAccountAvatar:'/static/img/default-account-avatar.jpg'
		},
		onLaunch: function() {
			let that = this;
			// 系统默认配置
			uni.getSystemInfo({
				success: function(e) {
					// 上导航的高度自适应
					// #ifndef MP
					Vue.prototype.StatusBar = e.statusBarHeight;
					if (e.platform == 'android') {
						Vue.prototype.CustomBar = e.statusBarHeight + 50;
					} else {
						Vue.prototype.CustomBar = e.statusBarHeight + 45;
					};
					// #endif

					// #ifdef MP-WEIXIN
					Vue.prototype.StatusBar = e.statusBarHeight;
					let custom = wx.getMenuButtonBoundingClientRect();
					Vue.prototype.Custom = custom;
					let customBar = custom.bottom + custom.top - e.statusBarHeight + 4;
					Vue.prototype.CustomBar = customBar;
					that.globalData.CustomBar = customBar;
					// #endif	

					// #ifdef MP-ALIPAY
					Vue.prototype.StatusBar = e.statusBarHeight;
					Vue.prototype.CustomBar = e.statusBarHeight + e.titleBarHeight;
					// #endif
				}
			});
		},
		onShow: function() {
			console.log('App Show')
		},
		onHide: function() {
			console.log('App Hide')
		},
		methods: {
		}
	}
</script>

<style>
	/* #ifndef APP-PLUS-NVUE */
	@import "./app.css";
	/* #endif */

	.status_bar {
		height: var(--status-bar-height);
		width: 100%;
	}
</style>