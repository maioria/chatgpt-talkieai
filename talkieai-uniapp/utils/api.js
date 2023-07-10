import __config from '@/config/env';
const request = (url, method, data, showLoading) => {
	let _url = __config.basePath + url
	return new Promise((resolve, reject) => {
		if (showLoading) {
			uni.showLoading();
		}
		uni.request({
			url: _url,
			method: method,
			data: data,
			header: {
				'Content-Type': 'application/json',
				'X-Token': uni.getStorageSync('x-token') ? uni.getStorageSync(
					'x-token') : '',
			},
			success(res) {
				if (res.statusCode == 200) {
					if (res.data.code == '200') {
						resolve(res.data);
					} else {
						uni.showToast({
							title: res.data.message,
							icon: 'none'
						})
						reject(res.data)
					}
					return;
				} else if (res.statusCode == 401) { // 401代表用户登录信息不正确，清除登录信息后重新到默认页面触发游客登录
					uni.setStorageSync('x-token', '');
					uni.redirectTo({
						url: '/pages/index/entrance'
					})
				} else {
					reject(res.data)
				}
			},
			fail(error) {
				console.error(error);
				reject(error);
			},
			complete(res) {
				uni.hideLoading();
			}
		});
	});
}

export default {
	request,
	getLanguageDemoContent: data => {
		return request('/language-demo-content', 'post', data, false);
	},
	visitorLogin: data => {
		return request('/visitor-login', 'post', data, true);
	},
	getUserInfo: data => {
		return request('/user-info', 'get', data, true);
	},
	getUserInfoUsage: data => {
		return request('/user-info/usage', 'get', data, true);
	},
	sessionCreate: data => {
		return request('/sessions', 'post', data, true);
	},
	sessionCount: data => {
		return request('/sessions/count', 'get', data, true);
	},
	sessionPage: data => {
		return request('/sessions', 'get', data, true);
	},
	sessionGet: data => {
		return request('/sessions/' + data.sessionId, 'get', data, true);
	},
	sessionDelete: data => {
		return request('/sessions/' + data.sessionId, 'delete', data, true);
	},
	sessionMessagesGet: data => {
		return request('/sessions/' + data.sessionId + '/messages', 'get', data, true);
	},
	chatInvoke: data => {
		return request('/chat', 'post', data, false);
	},
	translateInvoke: data => {
		return request('/translate', 'post', data, false);
	},
	deleteLatestMessages: data => {
		return request('/sessions/' + data.sessionId + '/messages/latest', 'delete', data, true);
	},
	deleteAllMessages: data => {
		return request('/sessions/' + data.sessionId + '/messages', 'delete', data, true);
	},
	grammarInvoke: data => {
		return request('/grammar', 'post', data, false);
	},
	promptInvoke: data => {
		return request('/prompt', 'post', data, false);
	},
	transferSpeech: data => {
		return request('/speech', 'post', data, false);
	},
	speechDemo: data => {
		return request('/speech-demo', 'post', data, false);
	},
	supportLanguegas: data => {
		return request('/voices', 'get', data, true);
	}
}