<template>
	<view class="chat-entrance-container">
		<view class="title-box text-center margin-top-xl">
			<view class="xw-chat-entrance-title xw-text-blue">
				Talkie-AI
			</view>
			<view class="xw-chat-entrance-sub-title xw-text-blue margin-top-xs">
				陪你学英语
			</view>
			<view class="margin-top-xl xw-text-gray">
				练习口语、写作的好帮手
			</view>
		</view>

		<view class="button-box text-center">
			<view class="padding flex flex-direction">
				<button @tap="handleCreateSessionShow" class="cu-btn xw-bg-blue margin-tb-sm lg">开始新会话</button>
				<button v-if="sessionCount>0" @tap="handleSessionListShow"
					class="cu-btn xw-text-blue margin-tb-sm lg">历史会话（{{sessionCount}}）</button>
				<button @tap="handleProfile" class="cu-btn xw-text-blue margin-tb-sm lg">个人中心</button>
			</view>
		</view>

		<!-- 历史会话列表 -->
		<view class="cu-modal" :class="sessionListShow?'show':''">
			<view class="cu-dialog">
				<view class="cu-bar bg-white justify-end">
					<view class="content"></view>
					<view class="action" @tap="handleSessionListShow">
						<text class="cuIcon-close text-blue"></text>
					</view>
				</view>
				<scroll-view scroll-y="true" style="max-height: 65vh;">
					<view class="cu-list menu-avatar">
						<view v-for="item in sessionList" class="cu-item" @tap="handleDirectSession(item.id)">
							<image class="cu-avatar round lg" mode="aspectFill"
								:src="getTeacherAvatar(item.teacher_avatar, item.gender, item.feel)">
							</image>
							<view class="content">
								<view class="text-grey">
									{{item.name}}
									<text class="cu-tag round bg-grey sm">{{item.message_count}}</text>
								</view>
								<view class="text-gray text-sm flex">
									<view class="text-cut">
										{{item.friendly_time}}
									</view>
								</view>
							</view>
							<view class="action">
								<view class="text-grey text-xs">
									<button class="cu-btn cuIcon" @click.stop="handleDeleteSession(item)">
										<text class="cuIcon-delete"></text>
									</button>
								</view>
							</view>
						</view>
					</view>
				</scroll-view>
			</view>
		</view>
		<!-- 创建会话 -->
		<view class="cu-modal" :class="createSession.show?'show':''">
			<view class="cu-dialog">
				<view class="cu-bar bg-white justify-end">
					<view class="content">创建新会话</view>
					<view class="action" @tap="handleCreateSessionShow">
						<text class="cuIcon-close text-blue"></text>
					</view>
				</view>
				<view class="padding-tb-xl">
					<form>
						<view class="cu-form-group margin-top text-right">
							<view class="title">标题</view>
							<input v-model="createSession.form.name" placeholder="标题" name="input"></input>
						</view>
						<view class="cu-form-group">
							<view class="title">语言</view>
							<picker mode="multiSelector" @change="handleLanguageChange"
								@columnchange="handleLanguageColumnChange" :value="language.index"
								:range="language.range">
								<view class="picker" v-if="language.countryGroupList.length>0">
									{{currentLanguageLabel}}
								</view>
							</picker>
						</view>
						<view class="cu-form-group">
							<view class="title">角色</view>
							<picker mode="multiSelector" @change="handleLanguageRoleChange"
								@columnchange="handleLanguageRoleColumnChange" :value="language.roleIndex"
								:range="language.roleRange">
								<view class="picker">
									{{currentRoleLabel}}
								</view>
							</picker>
						</view>
						<view class="cu-form-group">
							<view class="title">语速</view>
							<view class="padding" style="flex:1;">
								<u-slider v-model="speechRateIndex" :step="5" :min="5"></u-slider>
							</view>
						</view>
						<view class="cu-form-group">
							<view class="title">试听</view>
							<view class="padding text-left" style="flex:1;">
								{{languageDemoContent}}
							</view>
							<button class="cu-btn bg-grey text-white" :class="{'cuIcon-sound':!audio.loading}"
								@tap="handlePlayDemo()">
								<text v-if="audio.loading" class="cuIcon-loading2 cuIconfont-spin"></text>
							</button>
							<!-- <text @tap="handlePlayDemo" class='cuIcon-sound text-gray'></text> -->
						</view>

					</form>
				</view>
				<view class="cu-bar bg-white justify-end">
					<view class="action">
						<button class="cu-btn line-blue text-green" @tap="handleCreateSessionShow">取消</button>
						<button class="cu-btn bg-blue margin-left" @tap="handleCreateSessionConfirm">确定</button>
					</view>
				</view>
			</view>
		</view>
		<!-- 页面上无元素，播放音频用 -->
		<audio-player ref="audioPlayer"></audio-player>
	</view>
</template>

<script>
	import api from '@/utils/api';
	const app = getApp();
	import shared from './components/share.js';
	import {
		supportLanguageMap,
		voiceStyleMap,
		language_demo_map,
		azure_voices_data
	} from './components/azure_voices_data.js';
	import __config from '@/config/env';
	import AudioPlayer from './components/AudioPlayer.vue';
	import Fingerprint2 from 'fingerprintjs2';
	const X_TOKEN = 'x-token';
	export default {
		components: {
			AudioPlayer,
		},
		mixins: [shared],
		computed: {
			currentRoleLabel() {
				const self = this;
				if (self.language.countryRoles.length === 0) {
					return '';
				}
				let currentRole = self.language.countryRoles[self.language.roleIndex[0]];
				let result = currentRole.local_name;
				let roleStyle = self.getCurrentRoleStyle();

				if (roleStyle) {
					result += ' / ' + voiceStyleMap[roleStyle]
				}
				console.log(result);
				return result;
			},
			currentLanguageLabel() {
				const self = this;
				return self.getCurrentLanguage().label
			}
		},
		data() {
			return {
				globalData: app.globalData,
				// 语言选择框
				language: {
					range: [],
					countryGroupList: [],
					index: [
						[0],
						[0]
					],
					countryRoles: [],
					countryRoleStyles: [],
					roleRange: [],
					roleGroupMap: [],
					roleIndex: [
						[0],
						[0]
					]
				},
				createSession: {
					show: false,
					form: {
						name: 'Talkie',
						gender: null,
						language: null,
						speech_role_name: null,
						speech_rate: '1.0',
						speech_style: '',
						teacherAvatar: ''
					}
				},
				sessionCount: 0,
				sessionListShow: false,
				sessionList: [],
				speechRateIndex: 50,
				// 默认是英文
				languageDemoContent: 'Hello, welcome to Talkie. We hope you have a good learning experience.',
				audio: {
					loading: false
				}
			}
		},
		onShow() {
			// 检查是否存在上一次的session，如果存在可以能过上次session继续进行
			api.sessionCount().then(data => {
				if (data.code === '200') {
					this.sessionCount = data.data
				}
			})
		},
		onLoad() {
			// 是否有保存登录的token
			let self = this;
			let storageToken = uni.getStorageSync(X_TOKEN);
			if (storageToken) {
				self.loginSucessByToken(storageToken);
			} else {
				// 进行访客登录
				self.handleVisitorLogin();
			}
		},
		methods: {
			handleVisitorLogin() {
				let self = this;
				if (self.loginLoading) {
					return;
				}
				// 获取设备指纹
				self.loginLoading = true;
				Fingerprint2.get((components) => {
					const values = components.map(component => component.value);
					const fingerprint = Fingerprint2.x64hash128(values.join(''), 31);

					// 在这里可以将设备指纹发送到服务器进行处理
					console.log('设备指纹:', fingerprint);

					api.visitorLogin({
						fingerprint: fingerprint
					}).then(data => {
						self.loginSuccess(data)
					}).finally(() => {
						self.loginLoading = false;
					})
				});
			},
			/**
			 * 用户登录请求结果处理
			 */
			loginSuccess(data) {
				let self = this;
				if (data.code !== '200') {
					uni.showToast({
						title: data.message,
						icon: 'none'
					});
					return;
				}
				let storageToken = data.data;
				self.loginSucessByToken(storageToken);
			},
			/**
			 * 通过用户token加载后续逻辑
			 */
			loginSucessByToken(storageToken) {
				let self = this;
				uni.setStorageSync('x-token', storageToken);
				self.globalData.xToken = storageToken;
				api.getUserInfo().then(data => {
					self.globalData.userInfo = data.data;
					uni.redirectTo({
						url: '/pages/index/entrance'
					});
					// 获取完用户信息后加载国家数据
					self.initLanguageData();
				})
			},
			/**
			 * 播放demo的效果
			 */
			handlePlayDemo() {
				const self = this;
				const form = {};
				form.language = self.getCurrentLanguage().key;
				form.speech_role_name = self.getCurrentRole().short_name;
				form.speech_rate = (self.speechRateIndex / 50).toFixed(1).toString();
				if (self.getCurrentRoleStyle()) {
					form.speech_style = self.getCurrentRoleStyle();
				}
				self.audio.loading = true;
				api.speechDemo(form).then(data => {
					const fileName = data.data.file;
					self.$refs.audioPlayer.playAudio({
						audioUrl: fileName,
						success: () => {
							self.audio.loading = false;
							console.log('success');
						},
						error: () => {
							self.audio.loading = false;
							console.log('error');
						}
					});
				});
			},
			initLanguageData() {
				let self = this;
				// 初始化国家下的角色与情绪数据，需要先初始化，后续根据内容过滤国家信息，角色中没有有国家信息需要过滤
				const groupedVoices = {};
				// Iterate over each voice
				azure_voices_data.forEach((voice) => {
					const {
						locale
					} = voice;

					// If the locale is not present in the groupedVoices object,
					// create an array for that locale
					if (!groupedVoices.hasOwnProperty(locale)) {
						groupedVoices[locale] = [];
					}

					// Push the voice to the respective locale array
					groupedVoices[locale].push(voice);
				});

				const languageMap = supportLanguageMap;
				// 去掉语言列表不存在的国家语言, 去掉相同value的语言
				const uniqueLanguageMap = {};
				for (const key in supportLanguageMap) {
					if (!groupedVoices.hasOwnProperty(key)) {
						continue;
					}
					const value = supportLanguageMap[key];
					if (!Object.values(uniqueLanguageMap).includes(value)) {
						uniqueLanguageMap[key] = value;
					}
				}

				// 对语言进行分组
				let groupedLanguages = [];
				for (const key in uniqueLanguageMap) {
					const countryCode = key.split('-')[0];
					const label = uniqueLanguageMap[key].split(/（|\(/)[0];
					const language = {
						key: key,
						label: uniqueLanguageMap[key]
					};

					// Check if the country code already exists in the groupedLanguages array
					const groupIndex = groupedLanguages.findIndex(group => group.key === countryCode);
					if (groupIndex !== -1) {
						// Country code exists, add language to the existing group
						groupedLanguages[groupIndex].list.push(language);
					} else {
						// Country code does not exist, create a new group
						groupedLanguages.push({
							key: countryCode,
							list: [language],
							label: label
						});
					}
				}

				self.language.countryGroupList = groupedLanguages;
				self.language.roleGroupMap = groupedVoices;

				// 加载range的初始内容
				self.initLanguageLabelRange();
			},
			getCurrentLanguage() {
				const self = this;
				const currentLanguage = self.language.countryGroupList[self.language.index[0]];
				const currentCountry = currentLanguage.list[self.language.index[1]]
				return currentCountry;
			},
			initLanguageLabelRange() {
				let self = this;
				const languageList = self.language.countryGroupList.map(item => self.removeParentheses(item
					.label));
				const countryLabelList = self.language.countryGroupList[self.language.index[0]]
					.list.map(
						item => item
						.label);
				self.language.range = [languageList, countryLabelList]
				self.initLanguageRoleRange();
			},
			initLanguageRoleRange() {
				const self = this;
				const currentLanguage = self.getCurrentLanguage();
				const countryRoles = self.language.roleGroupMap[currentLanguage.key];

				const roleLabels = countryRoles.map(item => {
					// gender 1:女 2: 男
					return item.local_name + '(' + (item.gender === 1 ? '♀' : '♂') + ')';
				});
				const roleStyles = countryRoles[self.language.roleIndex[0]].style_list;
				self.language.countryRoles = countryRoles;
				self.language.countryRoleStyles = roleStyles;

				let styleLabels = [];
				if (roleStyles.length > 0 && roleStyles[0].trim() !== '') {
					styleLabels = roleStyles.map(item => voiceStyleMap[item]);
				} else {
					styleLabels = ['默认']
				}
				self.language.roleRange = [roleLabels, styleLabels]
			},
			getCurrentRole() {
				const self = this;
				return self.language.countryRoles[self.language.roleIndex[0]];
			},
			getCurrentRoleStyle() {
				const self = this;
				if (self.language.countryRoleStyles.length > 0) {
					return self.language.countryRoleStyles[self.language.roleIndex[1]];
				}
				return null;
			},
			handleLanguageChange(e) {
				let self = this;
				self.language.index = e.target.value;
				self.initLanguageRoleRange();
			},
			handleLanguageColumnChange(e) {
				let self = this;
				// temp_value触发动态更新
				let temp_value = [self.language.index[0], self.language.index[1]];
				temp_value[e.detail.column] = e.detail.value;
				self.language.index = temp_value;
				// self.language.index[e.detail.column] = e.detail.value;
				if (e.detail.column === 0) {
					self.language.index[1] = 0;
					self.language.roleIndex = [0, 0];
					self.initLanguageLabelRange();
					// 语言有变更时，演示内容相应更新
					self.initDemoContent();
				}
				// 加载角色的初始信息
				self.initLanguageRoleRange();

			},
			handleLanguageRoleChange(e) {
				let self = this;
				self.language.roleIndex = e.target.value;
			},
			handleLanguageRoleColumnChange(e) {
				let self = this;
				// temp_value触发动态更新
				let temp_value = [self.language.roleIndex[0], self.language.roleIndex[1]];
				temp_value[e.detail.column] = e.detail.value;
				self.language.roleIndex = temp_value;
				if (e.detail.column === 0) {
					self.language.roleIndex[1] = 0;
					self.initLanguageRoleRange();
				}
				console.log(self.language.roleIndex)
			},
			initDemoContent() {
				const self = this;
				const language = self.getCurrentLanguage().key;
				self.languageDemoContent = language_demo_map[language.split('-')[0]];
			},
			/**
			 * 替换掉最后的括号, 包括中文与英文的
			 */
			removeParentheses(str) {
				// 匹配最后一对括号及其内容的正则表达式
				const regex = /\([^()]*\)$|\（[^()]*\）$/;

				// 使用空字符串替换匹配到的内容
				return str.replace(regex, '');
			},
			handleDeleteSession(session) {
				let self = this;
				uni.showModal({
					title: '提示',
					content: '确认删除吗？',
					success: function(res) {
						if (res.confirm) {
							api.sessionDelete({
								sessionId: session.id
							}).then(data => {
								let title = data.data ? '删除成功' : '删除失败';
								uni.showToast({
									title: title
								})
								self.initSessionList();
							})
						} else if (res.cancel) {}
					}
				})
			},
			handleSessionListShow() {
				let self = this;
				if (!self.sessionListShow) {
					this.initSessionList();
				}
				this.sessionListShow = !this.sessionListShow;
			},
			handleProfile() {
				uni.redirectTo({
					url: '/pages/profile/index'
				});
			},
			initSessionList() {
				api.sessionPage().then(data => {
					this.sessionList = data.data.list;
				})
			},
			handleCreateSessionShow() {
				this.createSession.show = !this.createSession.show;
			},
			handleCreateSessionConfirm() {
				// 创建新的会话，跳转到聊天
				let self = this;
				if (!self.createSession.form.name) {
					uni.showToast({
						title: '名称不能为空',
						icon: 'none'
					})
					return;
				}
				let createSession = self.createSession;
				let form = createSession.form;
				form.gender = self.getCurrentRole().gender == '1' ? 'FEMALE' : 'MALE';
				form.language = self.getCurrentLanguage().key;
				form.speech_role_name = self.getCurrentRole().short_name;
				// 提交rate为0.1到2.0，插件为1到100
				form.speech_rate = (self.speechRateIndex / 50).toFixed(1).toString();
				// form.speech_rate = self.speechRatePicker[self.speechRateIndex];
				if (self.getCurrentRoleStyle()) {
					form.speech_style = self.getCurrentRoleStyle();
				}
				api.sessionCreate(form).then(data => {
					if (data.code === '200') {
						uni.redirectTo({
							url: '/pages/index/chat?sessionId=' + data.data
						})
					}
				})
			},
			handleDirectSession(sessionId) {
				uni.redirectTo({
					url: '/pages/index/chat?sessionId=' + sessionId
				})
			}
		}
	}
</script>

<style lang="scss">
	.chat-entrance-container {
		.title-box {
			padding-top: 120upx;

			.xw-chat-entrance-title {
				font-size: 36px;
				font-weight: 400;
			}

			.xw-chat-entrance-sub-title {
				font-size: 18px;
				font-weight: 400;
			}
		}

		.button-box {
			margin-top: 70upx;
		}
	}

	.xw-text-blue {
		color: #4390F6;
	}

	.xw-text-gray {
		color: #333;
	}

	.xw-bg-blue {
		background-color: #4390F6;
		color: white;
	}

	.cu-modal {
		z-index: 101;
	}
</style>