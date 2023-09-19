<template>
    <img class="github-link" @tap="redirectToGithub" target="_blank" style="height: 32rpx; width: 32rpx;"
        src="/static/github/github-mark.png" alt="GitHub Logo" />
</template>
<script setup lang="ts">
const redirectToGithub = () => {
    const redirectUrl = 'https://github.com/maioria/chatgpt-talkieai/issues';
    // h5
    // #ifdef H5
    window.open(redirectUrl);
    // #endif
}
</script>
<style lang="scss" scoped>
.github-link {
    // bottom: 130rpx;
    // padding-bottom: calc(env(safe-area-inset-bottom) / 2);
    // position: fixed;
    // width: 100%;
    display: flex;
    justify-content: center;

    .github-logo {
        margin-left: 14rpx;
    }
}
</style>