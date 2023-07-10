<template>
	<view>
		<cu-custom bgColor="bg-gradual-blue" :isBack="true" :backFn="handleBackToEntrance">
			<block slot="content">
				聊天
			</block>
			<block slot="right">
				<view class="margin-right text-xl">
					<text @tap="handleSettingsModal" class="lg text-white cuIcon-settings"></text>
				</view>
			</block>
		</cu-custom>
		<view class="content">
			<scroll-view id="msg-box" class="msg-list" :style="[{top:currentCustomBar+'px'}]" scroll-y="true"
				:scroll-with-animation="scrollAnimation" :scroll-top="scrollTop" :scroll-into-view="scrollToView"
				upper-threshold="50">
				<view class="row" v-for="(item, index) in contents" :key="index" :id="'msg_' + index">
					<!-- 系统提示 -->
					<block v-if="item.role==='SYSTEM'">
						<view class="system">
							<view class="text">
								{{item.content}}
							</view>
						</view>
					</block>

					<block v-else>
						<!-- 用户消息 -->
						<view class="my" v-if="item.role==='USER'">
							<view class="left">
								<text class="bubble">
									<!-- rich-text在小程序上会不出现，暂时使用text -->
									<!-- <rich-text :nodes="item.content"></rich-text> -->
									<text>{{item.content}}</text>
								</text>
								<view class="tool-box">
									<!-- 播放声音 -->
									<button v-if="item.voiceFileName" class="cu-btn bg-grey text-white"
										:class="{'cuIcon-sound':!item.speechLoading}" @tap="handleUserSpeech(item)">
										<text v-if="item.speechLoading" class="cuIcon-loading2 cuIconfont-spin"></text>
									</button>
									<!-- 翻译成中文 -->
									<button v-if="!isChineseSession" class="cu-btn bg-grey text-white margin-left-sm"
										@tap="handleTranslate(item)">
										<text v-if="item.translateLoading"
											class="cuIcon-loading2 cuIconfont-spin"></text>
										<text v-else>
											译
										</text>
									</button>
									<!-- 语法分析 -->
									<button v-if="!isChineseSession" class="cu-btn bg-grey text-white margin-left-sm"
										@tap="handleGrammar(item)">
										<text v-if="item.grammarLoading" class="cuIcon-loading2 cuIconfont-spin"></text>
										<text v-else>
											语法
										</text>
									</button>
								</view>
							</view>
							<view class="right">
								<image v-if="globalData.userInfo.avatar_url" mode="aspectFill"
									:src="globalData.userInfo.avatar_url"></image>
								<image v-else mode="aspectFill" :src="globalData.defaultAccountAvatar"></image>
							</view>
						</view>

						<!-- 系统消息 -->
						<view class="other" v-if="item.role==='ASSISTANT'">
							<view class="left">
								<image mode="aspectFill"
									:src="getTeacherAvatar(sessionData.avatar, sessionData.gender, sessionData.feel)">
								</image>
							</view>
							<view class="right">
								<view class="username">
									<view class="name">Talkie</view>
									<view class="time">{{item.createTime}}</view>
								</view>
								<text class="bubble">
									<!-- rich-text在小程序上会不出现，使用text -->
									<!-- <rich-text :nodes="item.content"></rich-text> -->
									<text>{{item.content}}</text>
									<template v-if="!item.ended">
										<text class="blink-cursor">|</text>
									</template>
								</text>
								<view class="tool-box">
									<!-- 系统转语音 -->
									<button v-if="item.ended" class="cu-btn bg-grey text-white"
										:class="{'cuIcon-sound':!item.speechLoading}" @tap="handleSpeech(item)">
										<text v-if="item.speechLoading" class="cuIcon-loading2 cuIconfont-spin"></text>
									</button>
									<!-- 翻译成中文 -->
									<button v-if="!isChineseSession && item.ended"
										class="cu-btn bg-grey text-white margin-left-sm" @tap="handleTranslate(item)">
										<text v-if="item.translateLoading"
											class="cuIcon-loading2 cuIconfont-spin"></text>
										<text v-else>
											译
										</text>
									</button>
								</view>
							</view>
						</view>
					</block>

					<!-- 展示翻译完的中文 -->
					<view v-if="item.translateContentShow" class="system">
						<text class="text">
							{{item.translateContent}} <span @tap="handleHideTransition(item)"
								class="margin-left-xs text-blue">收起</span>
						</text>
					</view>

					<!-- 展示语法分析的结果 -->
					<view v-if="item.grammarContentShow" class="system">
						<text class="text">
							{{item.grammarContent}} <span @tap="handleHideGrammar(item)"
								class="margin-left-xs text-blue">收起</span>
						</text>
					</view>

					<!-- 展示音标的结果 -->
					<view v-if="item.phoneticContentShow" class="system">
						<text class="text">
							{{item.phoneticContent}} <span @tap="handleHidePhonetic(item)"
								class="margin-left-xs text-blue">收起</span>
						</text>
					</view>
				</view>

				<!-- 系统出现问题 -->
				<view class="row">
					<block v-if="assistantError">
						<view class="system">
							<view class="text">
								啊哦～Talkie刚才在开小差你可以重新提交对话 <span @tap="handResend"
									class="margin-left-xs text-blue">重新提交</span>
							</view>
						</view>
					</block>
				</view>

				<!-- 数据请求中 -->
				<view class="row">
					<block v-if="assistantLoading">
						<view class="system">
							<view class="text">
								Talkie正在思考ing～
							</view>
						</view>
					</block>
				</view>
			</scroll-view>
			<view class="cu-bar foot input" :style="[{bottom:InputBottom+'px'}]">
				<view class="action">
					<text @tap="handleSwitchInputType" class="text-grey"
						:class="inputType==='KEYBOARD'?'cuIcon-voicefill':'cuIcon-keyboard'"></text>
				</view>
				<template v-if="inputType==='KEYBOARD'">
					<input class="solid-bottom" v-model="inputValue" :adjust-position="false" :focus="false"
						@focus="InputFocus" @blur="InputBlur" maxlength="300" cursor-spacing="10"
						@confirm="handleSend"></input>
					<button class="cu-btn bg-blue lg shadow" @tap="handleSend">发送</button>
				</template>
				<template v-else-if="inputType==='VOICE'">
					<template v-if="!recorder.start">
						<button @tap="handleVoiceStart" class="cu-btn block bg-blue lg" style="flex:1;">
							开始录音
						</button>
					</template>
					<template v-else-if="!recorder.remainingTime">
						<button class="cu-btn block bg-blue lg loading" style="flex:1;border-radius: 0;">
							准备中..
						</button>
					</template>
					<template v-else>
						<button v-if="recorder.processing" class="cu-btn block bg-blue lg loading"
							style="flex:1;border-radius: 0;">
							处理中..
						</button>
						<template v-else-if="recorder.remainingTime">
							<button @tap="handleEndVoice" class="cu-btn block bg-blue lg cu-load loading"
								style="flex:4;border-radius: 0;">
								发送（{{recorder.remainingTime}}）
							</button>
							<button @tap="handleCancleVoice" class="cu-btn block bg-blue lg"
								style="flex:1;border-radius: 0;">
								取消
							</button>
						</template>
					</template>
				</template>
				<button v-if="!isChineseSession" class="cu-btn bg-blue lg shadow margin-left-sm"
					@tap="handleShowPopupLayer">提示</button>
			</view>
		</view>

		<view class="popup-layer" :class="popupLayerClass" @touchmove.stop.prevent="discard">
			<view class="prompt-content cu-load" :class="promptLoading?'loading':''">
				{{promptContent}}
			</view>
		</view>

		<!-- settings modal -->
		<view class="cu-modal drawer-modal justify-start" :class="{'show':settingsShow}"
			:style="[{top:currentCustomBar+'px',height:'calc(100vh - ' + currentCustomBar + 'px)'}]"
			@tap="handleSettingsModal()">
			<view class="cu-dialog basis-lg" @tap.stop="">
				<form>
					<view class="cu-form-group margin-top">
						<view class="title">自动播放音频</view>
						<switch @change="handleSettingsAutoPlayVideo" :class="settings.autoPlayVideo?'checked':''"
							:checked="settings.autoPlayVideo"></switch>
					</view>

					<view class="cu-form-group margin-top">
						<button class="cu-btn bg-blue lg shadow block" @tap="handleDeleteLatestMessage()"
							:disabled='deleteLoading'>删除最近一次消息</button>
					</view>
					<view class="cu-form-group margin-top">
						<button class="cu-btn bg-blue lg shadow block" @tap="handleDeleteAllMessage()"
							:disabled='deleteLoading'>删除所有消息</button>
					</view>
				</form>
			</view>
			<!-- 页面上无元素，播放音频用 -->
			<audio-player ref="audioPlayer"></audio-player>
			<speech ref="speech"></speech>
		</view>
	</view>
</template>

<script>
	import api from '@/utils/api';
	import __config from '@/config/env';
	//通过import/require引入
	// #ifdef H5
	//必须引入的核心，换成require也是一样的。注意：recorder-core会自动往window下挂载名称为Recorder对象，全局可调用window.Recorder，也许可自行调整相关源码清除全局污染
	import Recorder from 'recorder-core';
	//需要使用到的音频格式编码引擎的js文件统统加载进来
	import 'recorder-core/src/engine/wav';
	// #endif
	import shared from './components/share.js';
	const app = getApp();
	const MAXIMUM_RECORDING_TIME = 60;
	import AudioPlayer from './components/AudioPlayer.vue';
	import Speech from './components/Speech.vue';
	export default {
		components: {
			AudioPlayer,
			Speech
		},
		mixins: [shared],
		computed: {
			isChineseSession() {
				return this.isChinese(this.sessionData)
			},
			currentCustomBar() {
				// #ifdef MP-WEIXIN
				return this.globalData.CustomBar
				// #endif	

				// #ifdef H5
				return this.CustomBar
				// #endif	
			}
		},
		data() {
			return {
				globalData: app.globalData,
				promopt: {
					show: false,
					text: '',
					promoptText: '',
					originalTranslate: true,
					loading: false
				},
				settingsShow: false,
				scrollAnimation: false,
				scrollTop: 0,
				scrollToView: '',
				contents: [],
				assistantError: false,
				assistantLoading: false,
				inputType: 'KEYBOARD', // or VOICE
				inputValueHistory: '',
				inputValue: '',
				voiceLoading: false,
				voiceFileName: null,
				inputBottom: 0,
				sessionId: '',
				sessionData: null,
				recorder: {
					start: false,
					processing: false,
					remainingTime: null,
					rec: null,
					wxRecorderManager: null
				},
				settingsShow: false,
				settings: {
					autoPlayVideo: false,
					voiceDirectSend: true
				},
				deleteLoading: false,
				// 抽屉参数
				popupLayerClass: '', // showLayer
				promptLoading: false,
				promptMessageId: null,
				promptContent: '',
				InputBottom: 0
			}
		},
		onLoad(option) {
			// 如果传递了sessionId，则赋值sessionId，并且加载最近20条数据
			let self = this;
			if (option.sessionId) {
				self.sessionId = option.sessionId
				api.sessionGet({
					sessionId: self.sessionId
				}).then(data => {
					self.sessionData = data.data
				})
				api.sessionMessagesGet({
					sessionId: option.sessionId,
					page: 1,
					page_size: 20
				}).then(data => {
					data.data.list.forEach(item => {
						self.pushContent({
							role: item.role,
							id: item.id,
							content: item.content,
							voiceFileName: item.file_name,
							createTime: item.create_time,
							ended: true
						})
					});
				})
			}
		},
		methods: {
			InputFocus(e) {
				this.InputBottom = e.detail.height;
			},
			InputBlur(e) {
				this.InputBottom = 0;
			},
			handleShowPopupLayer() {
				const self = this;
				if (!self.popupLayerClass) {
					self.promptContent = '';
					self.popupLayerClass = 'showLayer';
					const lastMessage = self.contents[self.contents.length - 1];
					if (lastMessage.type === 'account') {
						// 最后一条是用户返回的话需要等系统返回
						return;
					}
					self.promptLoading = true;
					api.promptInvoke({
						session_id: self.sessionId,
						message_id: lastMessage.id
					}).then(data => {
						self.promptLoading = false;
						self.promptMessageId = lastMessage.id;
						self.promptContent = data.data;
					});
				} else {
					self.popupLayerClass = '';
				}
			},
			discard() {
				return;
			},
			handleDeleteAllMessage() {
				let self = this;
				uni.showModal({
					title: '提示',
					content: '确认删除吗？',
					success: function(res) {
						if (res.cancel) {
							return; // 用户取消就直接返回
						}
						self.deleteLoading = true;
						api.deleteAllMessages({
							sessionId: self.sessionId
						}).then(data => {
							self.deleteLoading = false;
							self.contents = [];
						});
					}
				});
			},
			handleDeleteLatestMessage() {
				let self = this;
				uni.showModal({
					title: '提示',
					content: '确认删除吗？',
					success: function(res) {
						if (res.cancel) {
							return; // 用户取消就直接返回
						}
						self.deleteLoading = true;
						api.deleteLatestMessages({
							sessionId: self.sessionId
						}).then(data => {
							self.deleteLoading = false;
							self.removeObjectsById(data.data, self.contents);
						});
					}
				});
			},
			removeObjectsById(ids, objects) {
				for (let i = 0; i < objects.length; i++) {
					if (ids.includes(objects[i].id)) {
						objects.splice(i, 1);
						i--;
					}
				}
			},
			handleSwitchOriginalTranslate() {
				this.promopt.originalTranslate = !this.promopt.originalTranslate;
			},
			handlePromptShow() {
				this.promopt.show = !this.promopt.show;
			},
			handleBackToEntrance() {
				uni.redirectTo({
					url: '/pages/index/entrance'
				})
			},
			/**
			 * 用户设置: 录音后直接发送
			 */
			handleSettingsVoiceDirectSend(e) {
				this.settings.voiceDirectSend = e.detail.value
			},
			/**
			 * 用户设置: 切换自动播放音频
			 */
			handleSettingsAutoPlayVideo(e) {
				this.settings.autoPlayVideo = e.detail.value
			},
			/**
			 * 显示设置框
			 */
			handleSettingsModal() {
				this.settingsShow = !this.settingsShow;
			},
			/**
			 * 隐藏设置框
			 */
			hideSettingsModal() {
				this.settingsShow = false;
			},
			handleSwitchInputType() {
				if (this.inputType === 'KEYBOARD') {
					this.inputType = 'VOICE';
				} else {
					this.inputType = 'KEYBOARD';
				}
			},
			/**
			 * 开始进行语音
			 */
			handleVoiceStart() {
				let self = this;
				this.$refs.audioPlayer.stopAudio();
				self.recorder.start = true;
				this.$refs.speech.handleVoiceStart({
					sessionId: self.sessionData.id,
					processing: () => {
						console.log('proccessing--');
						self.recorder.processing = true;
					},
					success: ({
						inputValue,
						voiceFileName
					}) => {
						console.log('success')
						self.inputValue = inputValue;
						self.voiceFileName = voiceFileName;
						self.recorder.processing = false;
						self.recorder.start = false;
						if (self.settings.voiceDirectSend) {
							self.handleSend();
						}
					},
					interval: (interval) => {
						console.log(interval + '--')
						self.recorder.remainingTime = interval;
					},
					cancel: () => {
						self.recorder.processing = false;
						self.recorder.start = false;
					},
					error: (err) => {
						self.recorder.processing = false;
						self.recorder.start = false;
					}
				});
			},
			handleCancleVoice() {
				let self = this;
				self.$refs.speech.handleCancleVoice();
			},
			/**
			 * 录音结束
			 */
			handleEndVoice() {
				let self = this;
				self.$refs.speech.handleEndVoice();
			},
			/**
			 * 重新取回上次发送的信息，再次发送
			 */
			handResend() {
				let that = this;
				that.inputValue = that.inputValueHistory;
				that.handleSend();
			},
			handleSend() {
				let self = this;
				self.assistantError = false;
				if (!self.checkInput()) {
					return;
				}
				let message = self.inputValue;
				let voiceFileName = self.voiceFileName;
				// 加入消息，清空输入框
				let push_item = self.pushAndFlushUserContent(message, voiceFileName)


				// ********************** 微信小程序并不支持SSE   ******************************
				// let asssitant_item = self.pushAssistantContent(null, null, null);
				// self.invoke_chat_stream({
				// 	session_id: self.sessionId,
				// 	message: message,
				// 	file_name: self.file_name,
				// 	item: asssitant_item,
				// 	success: (data) => {
				// 		// 如果设置了自动转语音，在这里进行转换
				// 		console.log(data)
				// 		push_item.id = data.send_message_id
				// 		asssitant_item.id = data.id;
				// 		asssitant_item.ended = true;
				// 		if (self.settings.autoPlayVideo) {
				// 			self.$nextTick(() => {
				// 				self.handleSpeech(self.contents[self.contents.length - 1])
				// 			});
				// 		}
				// 	}
				// });
				// ********************** 微信小程序并不支持SSE   ******************************


				// 发送到服务端
				self.assistantLoading = true;
				api.chatInvoke({
						session_id: self.sessionId,
						message: message,
						file_name: self.voiceFileName
					})
					.then((data) => {

						// 用户发送也会生成 message_id，在这里进行补充
						data = data.data
						push_item.id = data.send_message_id
						self.sessionId = data.session_id;
						let item = self.pushAssistantContent(data.id, data.data, data.create_time);
						item.ended = true;
						// 如果设置了自动转语音，在这里进行转换
						if (self.settings.autoPlayVideo) {
							self.$nextTick(() => {
								self.handleSpeech(self.contents[self.contents.length - 1])
							});
						}
					}, (error) => {
						console.error('error', error)
						if (error.code == '403') {
							// 移除前面的信息
							this.contents.pop()
							return;
						}
						self.assistantError = true;
					}).finally(() => {
						self.voiceFileName = null;
						self.assistantLoading = false;
					});
			},
			/**
			 * 增加用户消息
			 * 清空当前输入数据，暂存历史数据
			 */
			pushAndFlushUserContent(content, voiceFileName) {
				let pushItem = {
					role: 'USER',
					content: content,
					voiceFileName: voiceFileName
				};
				this.pushContent(pushItem);
				this.inputValueHistory = this.inputValue;
				this.inputValue = '';
				return pushItem;
			},
			/**
			 * 增加系统消息
			 */
			pushAssistantContent(id, content, createTime) {
				return this.pushContent({
					role: 'ASSISTANT',
					id: id,
					content: content,
					createTime: createTime,
					ended: false
				});
			},
			/**
			 * 播放用户的声音
			 */
			handleUserSpeech(item) {
				let self = this;
				item.speechLoading = true;
				self.$refs.audioPlayer.playAudio({
					audioUrl: item.voiceFileName,
					success: () => {
						item.speechLoading = false;
					},
					error: () => {
						item.speechLoading = false;
					}
				});
			},
			/**
			 * item系统消息转为语音文件并且播放
			 */
			handleSpeech(item) {
				let self = this;
				item.speechLoading = true;
				// 如果转换过则直接播放
				if (item.speechContent) {
					self.$refs.audioPlayer.playAudio({
						audioUrl: item.speechContent,
						success: () => {
							item.speechLoading = false;
						},
						error: () => {
							item.speechLoading = false;
						}
					});
					return;
				}
				api.transferSpeech({
					message_id: item.id
				}).then(data => {
					data = data.data.file
					item.speechContent = data;
					// 播放
					self.$refs.audioPlayer.playAudio({
						audioUrl: data,
						success: () => {
							item.speechLoading = false;
						},
						error: () => {
							item.speechLoading = false;
						}
					});
				});
			},
			/**
			 * 隐藏翻译后的信息
			 */
			handleHideTransition(item) {
				item.translateContentShow = !item.translateContentShow;
			},
			/**
			 * 隐藏语法解析的结果
			 */
			handleHideGrammar(item) {
				item.grammarContentShow = !item.grammarContentShow;
			},
			/**
			 * 隐藏、显示音标的结果
			 */
			handleHidePhonetic(item) {
				item.phoneticContentShow = !item.phoneticContentShow;
			},
			/**
			 * 信息翻译成中文
			 */
			handleTranslate(item) {
				// 如果已经翻译过则直接显示
				if (item.translateContent) {
					item.translateContentShow = !item.translateContentShow;
					return;
				}
				item.translateLoading = true;
				api.translateInvoke({
					message_id: item.id,
					target_language: 'zh_CN'
				}).then(data => {
					item.translateContent = data.data;
					item.translateContentShow = true;
				}).finally(() => {
					item.translateLoading = false;
				});

			},
			handleGrammar(item) {
				// 如果已经翻译过则直接显示
				if (item.grammarContent) {
					item.grammarContentShow = !item.grammarContentShow;
					return;
				}
				item.grammarLoading = true;
				api.grammarInvoke({
					message_id: item.id
				}).then(data => {
					item.grammarContent = data.data;
					item.grammarContentShow = true;
				}).finally(() => {
					item.grammarLoading = false;
				});
			},

			/**
			 * 根据用户输入信息生成提示词
			 */
			handleGeneraPrompt() {
				let self = this;
				if (self.promopt.loading) {
					return;
				}
				if (!self.promopt.text) {
					uni.showToast({
						title: '需要输入提示内容！',
						icon: 'none'
					})
					return;
				}
				self.promopt.loading = true;
				api.promptInvoke({
					session_id: self.sessionId,
					text: self.promopt.text,
					original_translate: self.promopt.originalTranslate
				}).then(data => {
					self.promopt.promoptText = data.data;
				}).finally(() => {
					self.promopt.loading = false;
				});
			},
			handlePhonetic(item) {
				if (item.phoneticContent) {
					item.phoneticContentShow = !item.phoneticContentShow;
					return;
				}
				item.phoneticLoading = true;
				api.phoneticInvoke({
					message_id: item.id
				}).then(data => {
					item.phoneticContent = data.data;
					item.phoneticContentShow = true;
				}).finally(() => {
					item.phoneticLoading = false;
				});
			},
			/**
			 * 补充额外数据
			 * 是否语音转换中
			 * 语音转换结果
			 * 是否翻译转换中
			 * 翻译转换后的结果
			 */
			pushContent(object) {
				// 语音转换
				object.speechLoading = false;
				object.speechContent = null;
				// 翻译
				object.translateLoading = false;
				object.translateContent = null;
				object.translateContentShow = false;
				// 语法
				object.grammarLoading = false;
				object.grammarContent = null;
				object.grammarContentShow = false;
				// 音标
				object.phoneticLoading = false;
				object.phoneticContent = null;
				object.phoneticContentShow = false;

				this.contents.push(object);
				this.$nextTick(() => {
					this.scrollMessageList();
				})
				return object;
			},
			// 检查用户是否有输入内容
			checkInput() {
				if (this.assistantLoading) {
					return false;
				}
				if (!this.inputValue) {
					uni.showToast({
						title: '请输入内容！',
						icon: 'none'
					})
					return false;
				}
				return true;
			},
			/**
			 * 自动移动视图到最底
			 */
			scrollMessageList() {
				this.scrollToView = 'msg_' + (this.contents.length - 1)
			},
			/**
			 * SSE的方式获取返回信息
			 */
			invoke_chat_stream({
				session_id,
				message,
				file_name,
				item,
				success
			}) {
				let self = this;
				self.assistantLoading = true;
				stream_post({
					url: __config.basePath + '/chat-process',
					headers: {
						'X-Token': uni.getStorageSync('x-token') ? uni.getStorageSync(
							'x-token') : ''
					},
					data: {
						message: message,
						session_id: session_id,
						file_name: self.voiceFileName
					},
					onDownloadProgress: ({
						event
					}) => {
						console.log(event)
						const responseText = event.target.responseText.replace(/\n$/, '');;
						// 按照换行符分割字符串
						const lines = responseText.split('\n');

						// 获取最后一行字符串
						const lastLine = lines[lines.length - 1];

						// 去除最后的占位符
						const trimmedLastLine = lastLine.trim();

						// 解析为JSON对象
						const json = JSON.parse(trimmedLastLine);
						item.content = json.data;
						item.ended = (json.ended == 'true');
						if (item.ended) {
							success(json);
						}
					}
				}).then(data => {
					//
					console.log(data)
				}).finally(() => {
					self.voiceFileName = null;
					self.assistantLoading = false;
				});
			}
		}
	}
</script>

<style lang="scss">
	.content {
		width: 100%;
		padding-bottom: calc(env(safe-area-inset-bottom) / 2);

		.msg-list {
			width: 100%;
			padding: 0 2%;
			position: absolute;
			top: 0;
			bottom: 100upx;
			// padding-bottom: calc(env(safe-area-inset-bottom) / 2);

			.row {
				.system {
					display: flex;
					justify-content: center;

					view,
					text {
						margin-top: 15upx;
						padding: 15upx 30upx;
						min-height: 50upx;
						display: flex;
						justify-content: center;
						align-items: center;
						background-color: #c9c9c9;
						color: #fff;
						font-size: 24upx;
						border-radius: 40upx;
					}
				}

				&:first-child {
					margin-top: 20upx;
				}

				padding: 20upx 0;

				.left {
					.tool-box {
						text-align: right;
					}
				}

				.right {
					.tool-box {
						text-align: left;
					}
				}

				.my .left,
				.other .right {
					width: 100%;
					display: flex;
					position: relative;
					padding-bottom: 75upx;

					.bubble {
						max-width: 70%;
						min-height: 50upx;
						border-radius: 10upx;
						padding: 15upx 20upx;
						display: flex;
						align-items: center;
						font-size: 32upx;
						word-break: break-word;
					}

					.tool-box {
						position: absolute;
						bottom: 0;
						width: 100%;
					}

					&.voice {
						.icon {
							font-size: 40upx;
							display: flex;
							align-items: center;
						}

						.icon:after {
							content: " ";
							width: 53upx;
							height: 53upx;
							border-radius: 100%;
							position: absolute;
							box-sizing: border-box;
						}

						.length {
							font-size: 28upx;
						}
					}
				}

				.my .right,
				.other .left {
					flex-shrink: 0;
					width: 80upx;
					height: 80upx;

					image {
						width: 80upx;
						height: 80upx;
						border-radius: 10upx;
					}
				}

				.my {
					width: 100%;
					display: flex;
					justify-content: flex-end;

					.left {
						min-height: 80upx;

						align-items: center;
						justify-content: flex-end;

						.bubble {
							background-color: #f06c7a;
							color: #fff;
						}
					}

					.right {
						margin-left: 15upx;
					}
				}

				.other {
					width: 100%;
					display: flex;

					.left {
						margin-right: 15upx;
					}

					.right {
						flex-wrap: wrap;

						.bubble {
							background-color: #fff;
							color: #333;
						}

						.username {
							width: 100%;
							height: 45upx;
							line-height: 30upx;
							font-size: 24upx;
							color: #999;
							display: flex;

							.name {
								margin-right: 50upx;
							}
						}
					}
				}
			}
		}
	}

	page {
		padding-bottom: 100upx;
	}

	.cu-chat {
		padding-bottom: 120upx;

		.cu-item {
			.speech {
				position: absolute;
				color: #8799a3;
				width: calc(100% - 320upx);
				bottom: 0upx;
				left: 160upx;
			}

			.tranlation-box {
				position: absolute;
				width: calc(100% - 320upx);
				bottom: 0upx;
			}
		}
	}

	//  原本的cu-model z-index 1000+ 太高导致toast被遮住了
	.cu-bar.foot {
		z-index: 101;
		padding-bottom: calc(env(safe-area-inset-bottom) / 2);
	}

	.cu-modal {
		z-index: 201;
	}

	// 闪烁光标的效果
	.blink-cursor {
		animation: blink 1s infinite;
	}

	@keyframes blink {
		0% {
			opacity: 1;
		}

		50% {
			opacity: 0;
		}

		100% {
			opacity: 1;
		}
	}

	// 提示弹出层
	.popup-layer {
		&.showLayer {
			transform: translate3d(0, -43vw, 0);
		}

		transition: all .15s linear;
		width: 100%;
		height: 42vw;
		padding: 20upx 2%;
		background-color: #f3f3f3;
		border-top: solid 1upx #ddd;
		position: fixed;
		z-index: 20;
		top: 100%;
	}
</style>