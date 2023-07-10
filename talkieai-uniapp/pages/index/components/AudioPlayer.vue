<template>
</template>

<script>
	import __config from '@/config/env';
	export default {
		data() {
			return {
				audio: {
					innerAudioContext: null
				}, // 当前正在播放的音频对象
			};
		},
		methods: {
			// 停止正播放的音频
			stopAudio() {
				const audio = this.audio;
				if (audio.innerAudioContext) {
					// 当前组件正在播放不同音频，暂停当前音频并调用success，然后播放新的音频
					audio.innerAudioContext.stop();
					audio.innerAudioContext = null;
				}
			},
			playAudio({
				audioUrl,
				success,
				error
			}) {
				console.log(audioUrl)
				const self = this;
				const audio = self.audio;
				let audioSrc = __config.basePath + '/files/' + audioUrl;
				if (audio.innerAudioContext) {
					if (audio.innerAudioContext.src === audioSrc) {
						// 当前组件正在播放相同音频，暂停当前音频并调用success
						audio.innerAudioContext.stop();
						audio.innerAudioContext = null;
						return;
					} else {
						// 当前组件正在播放不同音频，暂停当前音频并调用success，然后播放新的音频
						audio.innerAudioContext.stop();
						audio.innerAudioContext = null;
					}
				}
				// #ifdef MP-WEIXIN
				audio.innerAudioContext = wx.createInnerAudioContext({
					useWebAudioImplement: true
				});
				// #endif
				// #ifdef H5
				audio.innerAudioContext = uni.createInnerAudioContext();
				// #endif
				// 创建新的音频对象
				audio.innerAudioContext.src = audioSrc;
				audio.innerAudioContext.autoplay = true;
				console.log(audio.innerAudioContext)
				// 监听音频可以播放的事件
				audio.innerAudioContext.onCanplay(() => {
					console.log('can play')
					// 在 onCanplay 回调中播放音频
					audio.innerAudioContext.play();
				});
				audio.innerAudioContext.onPlay(() => {
					console.log('play')
					self.audio.audioPlaying = true;
				});
				audio.innerAudioContext.onStop(() => {
					console.log('stop')
					audio.innerAudioContext = null;
					if (success) {
						success();
					}
				});
				audio.innerAudioContext.onEnded(() => {
					console.log('ended')
					// self.audio.innerAudioId = null;
					// if (audio.innerAudioContext) {
					// 	audio.innerAudioContext.destroy();
					audio.innerAudioContext = null;
					// }
					if (success) {
						success();
					}
				});
				audio.innerAudioContext.onError((res) => {
					// console.error(res);
					// if (audio.innerAudioContext) {
					// audio.innerAudioContext.destroy();
					audio.innerAudioContext = null;
					// }
					if (error) {
						error();
					}
				});
			},
		},
	};
</script>