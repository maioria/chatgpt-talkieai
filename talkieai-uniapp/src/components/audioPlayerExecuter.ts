import __config from "@/config/env";
import { ref } from "vue";

interface Listener {
  playing?: () => void;
  success?: () => void;
  error?: () => void;
}

class AudioPlayer {
  private audioContext: any = null;
  constructor() {}

  /**
   * 录音的时候使用，录音前要先关闭所有音频播放
   */
  stopAudio() {
    if (this.audioContext) {
      this.audioContext.stop();
    }
  }

  playAudio({ audioUrl, listener }: { audioUrl: string; listener: Listener }) {
    let audioSrc = audioUrl;
    if (this.audioContext) {
      console.log(this.audioContext.src);
    }
    if (this.audioContext) {
      console.log("destory.." + this.audioContext.src);
      const oldSrc = this.audioContext.src;
      this.audioContext.stop();
      // this.audioContext.destory && this.audioContext.destory();
      // this.audioContext.stop();
      // this.audioContext.pause();
      if (oldSrc === audioSrc) {
        this.audioContext = null;
        return;
      }
    }

    let innerAudioContext = this.createInnerAudioContext(audioUrl, listener);
    this.audioContext = innerAudioContext;
    innerAudioContext.play(); // 播放
  }

  createInnerAudioContext(src: string, listener: Listener) {
    let innerAudioContext: any = null;
    // #ifdef MP-WEIXIN
    innerAudioContext = wx.createInnerAudioContext({
      useWebAudioImplement: true,
    });
    // #endif

    // #ifndef MP-WEIXIN
    innerAudioContext = uni.createInnerAudioContext();
    // #endif

    innerAudioContext.src = src;

    innerAudioContext.onPlay(() => {
      console.log("onPlay");
      if (listener.playing) {
        listener.playing();
      }
    });
    innerAudioContext.onStop(() => {
      console.log("onStop");
      if (listener.success) {
        listener.success();
      }
      innerAudioContext.destory && innerAudioContext.destory();
      this.audioContext = null;
      // this.audioContext=null;
    });
    innerAudioContext.onEnded(() => {
      console.log("onEnded");
      if (listener.success) {
        listener.success();
      }
      console.log("end audio context1");
      innerAudioContext.destory && innerAudioContext.destory();
      this.audioContext = null;
      console.log("end audio context2");
      console.log(this.audioContext);
      // console.log("destory");
    });
    innerAudioContext.onError((res: any) => {
      console.log("onError");
      console.log(res);
      if (listener.error) {
        listener.error();
      }
    });
    return innerAudioContext;
  }
}

const audioPlayer = new AudioPlayer();
// export default audioPlayer;
export default audioPlayer;
