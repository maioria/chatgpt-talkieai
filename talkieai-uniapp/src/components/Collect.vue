<template>
    <view class="collect-icon-box">
        <LoadingRound v-show="collectLoading"></LoadingRound>
        <image @tap="handleCollect" v-show="!collectLoading && !collected" class="collect-icon"
            src="/static/icon_collect.png"></image>
        <image @tap="handleCancel" v-show="!collectLoading && collected" class="collect-icon"
            src="/static/icon_collect_actived.png">
        </image>
    </view>
</template>
  
<script setup lang="ts">
import { ref, onMounted } from 'vue';
import accountRequest from '@/api/account';
import LoadingRound from "@/components/LoadingRound.vue";
const app = getApp();

const props = defineProps<{
    type: String,
    messageId?: String,
    content?: String,
}>();


const collected = ref(false);
const collectLoading = ref(false);

const requestParams = {
    type: props.type,
    message_id: props.messageId ? props.messageId : '',
    content: props.content ? props.content : '',
};

onMounted(() => {
    if (!props.messageId && !props.content) {
        console.warn(`Collect组件需要传入messageId或content,当前传入的参数为${JSON.stringify(props)}`)
        return;
    }

    accountRequest.collectGet(requestParams).then((data) => {
        collected.value = data.data.is_collect;
    });
});

const handleCollect = () => {
    if (collectLoading.value) {
        return;
    }

    collectLoading.value = true;
    accountRequest.collect(requestParams).then(() => {
        collected.value = true;
        collectLoading.value = false;
    });
};

const handleCancel = () => {
    if (collectLoading.value) {
        return;
    }

    collectLoading.value = true;
    accountRequest.cancelCollect(requestParams).then(() => {
        collected.value = false;
        collectLoading.value = false;
    });
};
</script>
  
<style scoped lang="less">
.collect-icon-box {
    width: 32rpx;
    height: 30rpx;

    .collect-icon {
        width: 32rpx;
        height: 30rpx;
    }
}
</style>