<template>
	<view>
		<CommonHeader :leftIcon="true" :back-fn="handleBackPage" class="header" title="Talkie">
			<template v-slot:content>
				<text>反馈</text>
			</template>
		</CommonHeader>
		<view class="feedback">
			<view v-if="!pushStatus" class="feedback-box">
				<view class="feedback-textarea-box">
					<textarea class="feedback-textarea" v-model="content" placeholder="反馈意见可以是使用过程中遇到的问题，也可以是产品改进意见" />
					<!-- <textarea class="feedback-textarea" v-model="content" /> -->
					<!-- <view class="placeholder-style" v-if="content.length==0">反馈意见可以是使用过程中遇到的问题，也可以是产品改进意见</view> -->
				</view>
				<!-- <view class="feedback-input-box">
					<input class="feedback-input" v-model="contact" placeholder="留下你的手机号或微信，方便我们沟通联系" />
				</view> -->
				<view class="feedback-btn-box">
					<button @tap="handleAddFeedback" class="common-button feedback-btn">提交反馈</button>
				</view>
			</view>
			<view v-else class="feedback-box">
				<image class="feedback-ico" src="/static/feedback_success.png" />
				<view class="feedback-success">
					<text>提交成功</text>
				</view>
				<view class="feedback-btn-box">
					<button @tap="handleBackPage" class="common-button feedback-btn return-btn">返回</button>
				</view>
			</view>
		</view>
	</view>
</template>


<script setup lang="ts">
import CommonHeader from "@/components/CommonHeader.vue";
import { ref, reactive, onMounted } from "vue";
import sysRequest from '@/api/sys';

const pushStatus = ref(false);
const content = ref('');
const contact = ref('user');

onMounted(() => {
	uni.setNavigationBarTitle({
		title: 'TalkieAI'
	});
});

const handleAddFeedback = () => {
	// content与contact都不能为空
	if (!content.value) {
		// 为用户提示不能为空
		uni.showToast({
			title: '内容不能为空',
			icon: 'none',
			duration: 2000
		});
		return;
	}
	sysRequest.feedbackAdd({
		content: content.value,
		contact: contact.value,
	}).then(() => {
		pushStatus.value = true;
	});
}

/**
 * 回到主页面
 */
const handleBackPage = () => {
	uni.switchTab({
		url: "/pages/my/index",
	});
};
</script>
<style scoped src="./less/index.less" lang="less"></style>
