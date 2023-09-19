<template></template>
<script setup lang="ts">
import { ref } from "vue";

const innerAudioContext = ref(null);
interface Listener {
    playing?: () => void;
    success?: () => void;
    error?: () => void;
}

const play = ({ audioUrl, listener }: { audioUrl: string; listener: Listener }) => {
    if (innerAudioContext.value) {
        const oldSrc = innerAudioContext.value.src;
        innerAudioContext.value.stop();
        innerAudioContext.value = null;
        if (oldSrc === audioUrl) {
            return;
        }
    }

    let curInnerAudioContext = uni.createInnerAudioContext();
    curInnerAudioContext.src = audioUrl;
    curInnerAudioContext.autoplay = true;

    curInnerAudioContext.onCanplay(() => {
      console.log("onCanplay");
      curInnerAudioContext.play();
    });

    curInnerAudioContext.onPlay(() => {
      console.log("play");
      if (listener.playing) {
        listener.playing();
      }
    });
    curInnerAudioContext.onStop(() => {
      console.log("onStop");
      if (listener.success) {
        listener.success();
      }
    });
    curInnerAudioContext.onEnded(() => {
      console.log("onEnded");
      if (listener.success) {
        listener.success();
      }
    });
    curInnerAudioContext.onError((res: any) => {
      console.log("onError");
      if (listener.error) {
        listener.error();
      }
    });

    innerAudioContext.value = curInnerAudioContext;
}
defineExpose({
    play
});
</script>