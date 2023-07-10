<template>
	<view>
	</view>
</template>

<script>
	import __config from '@/config/env';
	const MAXIMUM_RECORDING_TIME = 60;
	export default {
		data() {
			return {
				recorder: {
					start: false,
					processing: false,
					remainingTime: null,
					rec: null,
					wxRecorderManager: null
				},
				sessionId: null,
				intervalId: null,
				listener: {
					success: null,
					cancel: null,
					error: null,
					interval: null
				}
			};
		},
		methods: {
			/**
			 * 开始进行语音
			 */
			handleVoiceStart({
				success,
				cancel,
				error,
				interval,
				processing,
				sessionId
			}) {
				let self = this;
				self.listener.success = success;
				self.listener.cancel = cancel;
				self.listener.error = error;
				self.listener.interval = interval;
				self.listener.processing = processing;
				self.sessionId = sessionId;
				// #ifdef MP-WEIXIN
				self.mpWeixinVoiceStart()
				// #endif

				// #ifdef H5
				self.h5VoiceStart()
				// #endif
			},
			mpWeixinVoiceStart() {
				let self = this;
				let recorderManager = wx.getRecorderManager();
				self.recorder.wxRecorderManager = recorderManager;
				recorderManager.start({
					duration: MAXIMUM_RECORDING_TIME * 1000,
					sampleRate: 44100,
					encodeBitRate: 192000,
					format: 'wav'
				});
				self.recorder.start = true;
				self.recorder.remainingTime = MAXIMUM_RECORDING_TIME;
				self.intervalId = setInterval(() => {
					if (self.recorder.remainingTime === 0) {
						// 取消计时器
						self.handleEndVoice({
							success
						})
					} else {
						if (self.listener.interval) {
							self.listener.interval(self.recorder.remainingTime)
						}
						self.recorder.remainingTime--;
					}
				}, 1000);

				// 语音成功后的逻辑需要写到这里
				recorderManager.onStop((res) => {
					self.handleProcessWxEndVoice({
						filePath: res.tempFilePath
					});
					// 小程序的filePath是个http地址，需要下载来处理
				});
			},
			clearInterval() {
				const self = this;
				console.log('clear interval!')
				console.log(self.intervalId)
				if (self.intervalId) {
					clearInterval(self.intervalId);
				}
			},
			h5VoiceStart() {
				let self = this;
				self.recorder.rec = Recorder({
					type: "wav",
					bitRate: 32,
					sampleRate: 32000
				});
				self.recorder.rec.open(() => {
					self.recorder.start = true;
					self.recorder.rec.start();
					self.recorder.remainingTime = MAXIMUM_RECORDING_TIME;
					self.intervalId = setInterval(() => {
						if (self.listener.interval) {
							self.listener.interval(self.recorder.remainingTime)
						}
						if (self.recorder.remainingTime === 0) {
							// 取消计时器
							clearInterval(self.intervalId);
							self.handleEndVoice()
						} else {
							self.recorder.remainingTime--;
						}
					}, 1000);
				}, (msg, isUserNotAllow) => {
					uni.showToast({
						title: '请开启录音权限',
						icon: 'none'
					})
					error(msg)
				})
			},
			handleCancleVoice() {
				let self = this;
				self.clearInterval();
				// #ifdef MP-WEIXIN
				if (self.recorder.wxRecorderManager) {
					self.recorder.wxRecorderManager.stop();
					self.recorder.start = false;
					self.recorder.processing = false;
					self.recorder.wxRecorderManager = null;
				}
				// #endif

				// #ifdef H5
				if (self.recorder.rec) {
					self.recorder.rec.stop(() => {
						self.recorder.start = false;
						self.recorder.processing = false;
						self.recorder.rec = null;
					});
				}
				// #endif
				if (self.listener.cancel) {
					self.listener.cancel();
				}

			},
			/**
			 * 录音结束
			 */
			handleEndVoice() {
				let self = this;
				self.clearInterval();
				// 如果正在处理语音中，则直接返回
				if (self.recorder.processing) {
					return;
				}
				// #ifdef MP-WEIXIN
				self.handleWxEndVoice();
				// #endif

				// #ifdef H5
				self.handleH5EndVoice();
				// #endif
			},
			handleWxEndVoice() {
				// 小程序直接调用stop就可以了，前面实例化的时候有监听程序会执行后面逻辑
				let self = this;
				self.recorder.wxRecorderManager.stop();
			},
			handleProcessWxEndVoice({
				filePath,
			}) {
				let self = this;
				if (self.listener.processing) {
					self.listener.processing();
				}
				// 创建文件上传请求
				wx.uploadFile({
					url: __config.basePath + '/sessions/' + self.sessionId +
						'/voice/upload', // 服务器的URL
					filePath: filePath, // 录音文件的临时路径
					header: {
						'X-Token': uni.getStorageSync('x-token')
					},
					name: 'file', // 服务器接收文件的字段名
					success: (res) => {
						var resData = res;
						self.handleUploadResult({
							resData
						})
					},
					fail(e) {
						console.error(e, '失败原因')
						uni.showToast({
							title: '上传失败',
							icon: 'none'
						})
						if (self.listener.error) {
							self.listener.error(e)
						}
					},
					complete: () => {
						self.recorder.start = false;
						self.recorder.processing = false;
						self.recorder.rec = null;
					}
				});
			},
			handleH5EndVoice() {
				let self = this;
				if (self.listener.processing) {
					self.listener.processing();
				}
				self.recorder.rec.stop((blob, duration) => {
					self.recorder.processing = true;
					var reader = new FileReader();
					reader.addEventListener("load", function() {}, false);
					reader.readAsDataURL(blob);
					let blobURL = window.URL.createObjectURL(blob);
					uni.uploadFile({
						file: blob,
						header: {
							'X-Token': uni.getStorageSync('x-token')
						},
						name: 'file',
						formData: {
							file: blob
						},
						url: __config.basePath + '/sessions/' + self.sessionId +
							'/voice/upload', //上传录音的接口
						success: (res) => {
							var resData = res;
							self.handleUploadResult({
								resData
							})
						},
						fail(e) {
							console.error(e, '失败原因')
							uni.showToast({
								title: '上传失败',
								icon: 'none'
							})
						},
						complete: () => {
							self.recorder.start = false;
							self.recorder.processing = false;
							self.recorder.rec = null;
						}
					});
				}, function(s) {
					if (error) {
						error(s);
					}
					console.error('结束出错');
				}, true);
			},
			handleUploadResult({
				resData
			}) {
				const self = this;
				if (resData.statusCode == 200) {
					let resultJson = JSON.parse(resData.data)
					if (resultJson.code != '200') {
						uni.showToast({
							title: resultJson.message,
							icon: 'none'
						});
						if (self.listener.error) {
							self.listener.error(resultJson)
						}
						return;
					}
					let dataJson = resultJson.data;
					if (self.listener.success) {
						self.listener.success({
							inputValue: dataJson.result,
							voiceFileName: dataJson.file
						})
					}
				}
			}
		}
	}
</script>

<style>
</style>