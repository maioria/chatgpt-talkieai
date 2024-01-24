<template>
    <view class="container">
        <CommonHeader :leftIcon="true" :back-fn="handleBackPage" backgroundColor="#F5F5FE">
            <template v-slot:content>
                <text>短语手册</text>
            </template>
        </CommonHeader>
        <view class="content">
            <view class="my-phrase-box phrase-box">
                <view class="phrase-title">
                    我保存的短语
                </view>
                <view class="phrase-box">
                    <Statement @deleteCollect="handleDeleteCollect" v-for="sentence in mySentenceList"
                        :collect="sentence" />
                </view>
            </view>
            <view class="topic-phrase-box phrase-box">
                <view class="phrase-title">
                    场景短语
                </view>
                <view class="phrase-box">
                    <Statement v-for="sentence in topicSentenceList" :collect="sentence" :cannotCancel="true" />
                </view>
            </view>
        </view>
    </view>
</template>

<script setup lang="ts">
import CommonHeader from "@/components/CommonHeader.vue";
import LoadingRound from "@/components/LoadingRound.vue";
import chatRequest from "@/api/chat";
import topicRequest from "@/api/topic";
import accountRequest from "@/api/account";
import { ref } from "vue";
import Statement from "@/pages/practice/components/Statement.vue";

import { onLoad } from "@dcloudio/uni-app";

const topicId = ref('');
const topicPhraseLoading = ref(false);
const myPhraseLoading = ref(false);
const topicPhrase = ref([]);
const myPhrase = ref([])
const mySentenceList = ref<Collect[]>([]);
const topicSentenceList = ref<Collect[]>([]);
import type { Collect } from "@/models/index";

onLoad((props) => {
    uni.setNavigationBarTitle({
		title: 'Talkie'
	});
    topicId.value = props.topicId;
    initData(props.topicId);
});

const initData = (topicId: string) => {
    getTopicPhrases({topic_id:topicId})
    getSen();
};

const getTopicPhrases = (params) => {
    if (topicPhraseLoading.value) return;
    topicPhraseLoading.value = true;
    topicRequest.getPhrase(params).then((data) => {
        topicPhraseLoading.value = false;
        topicPhrase.value = data.data;
        topicPhrase.value.forEach(item=>{
            topicSentenceList.value.push({
                content: item.phrase,
                translation: item.phrase_translation,
                message_id: null,
                type: "SENTENCE",
            })        
        });
    });

};

const getTopicPhrase = () => {
    if (topicPhraseLoading.value) return;
    topicPhraseLoading.value = true;
    topicRequest.getPhrase({ topic_id: topicId.value }).then((data) => {
        topicPhraseLoading.value = false;
        topicPhrase.value = data.data.list;
        topicPhrase.value.forEach(item=>{
            topicSentenceList.value.push({
                content: item.content,
                translation: item.translation,
                message_id: null,
                type: "SENTENCE",
            })        
        });
    });

};

const getSen = () => {
    if (myPhraseLoading.value) return;
    myPhraseLoading.value = true;
    let params = {
        page: 1,
        type: "SENTENCE",
    };
    accountRequest.collectsGet(params).then((data) => {
        mySentenceList.value = mySentenceList.value.concat(data.data.list);
    });
    myPhraseLoading.value = false;
};

const handleDeleteCollect = () => {
    getSen();
};
</script>
<style lang="scss" scoped>
.content {
    margin-top: 48rpx;

    .phrase-box {
        .phrase-title {
            margin-left: 32rpx;
            font-size: 36rpx;
        }
    }

    .topic-phrase-box {
        margin-top: 48rpx;
    }
}</style>