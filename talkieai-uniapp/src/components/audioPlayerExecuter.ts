import __config from "@/config/env";
import { ref } from "vue";

interface Listener {
  playing?: () => void;
  success?: () => void;
  error?: () => void;
}

class AudioPlayer {
  private audioContext: any = null;
  private isPlaying: any = false;
  constructor() {}

  stopAudio() {
    if (this.audioContext) {
      this.audioContext.stop();
      this.audioContext.destory && this.audioContext.destory();
    }
  }

  playAudio({ audioUrl, listener }: { audioUrl: string; listener: Listener }) {
    // let audioSrc = __config.basePath + "/files/" + audioUrl;
    // console.log(audioSrc);
    let audioSrc = audioUrl;
    if (this.audioContext) {
      console.log("stop start..");
      const oldSrc = this.audioContext.src;
      this.audioContext.stop();
      this.audioContext.pause();
      console.log("stop end..");
      this.audioContext.destory && this.audioContext.destory();
      if (oldSrc === audioSrc) {
        this.audioContext = null;
        return;
      }
    }

    let innerAudioContext = uni.createInnerAudioContext();
    console.log('start play audio' + audioSrc)
    innerAudioContext.src = audioSrc;
    innerAudioContext.autoplay = true;

    // innerAudioContext.onCanplay(() => {
    //   // innerAudioContext.play();
    // });

    innerAudioContext.onPlay(() => {
      console.log("play");
      this.isPlaying = true;
      if (listener.playing) {
        listener.playing();
      }
    });
    innerAudioContext.onStop(() => {
      console.log("onStop");
      if (listener.success) {
        listener.success();
      }
      // this.audioContext=null;
    });
    innerAudioContext.onEnded(() => {
      console.log("onEnded");
      if (listener.success) {
        listener.success();
      }
      this.audioContext.src = "";
      this.audioContext.destory && this.audioContext.destory();
      console.log("destory");
    });
    innerAudioContext.onError((res: any) => {
      // ios下如果error的话走这里
      console.log("onError");
      console.log(res);
      if (this.isPlaying) {
        if (listener.error) {
          listener.error();
        }
        return;
      }
      this.audioContext = uni.getBackgroundAudioManager();
      this.audioContext.title = "music";
      this.audioContext.singer = "music";
      this.audioContext.coverImgUrl =
        "https://qiniu-web-assets.dcloud.net.cn/unidoc/zh/music-a.png";
      this.audioContext.src = audioSrc;
      this.audioContext.autoplay = true;
      this.audioContext.onEnded(() => {
        console.log("onEnded");
        if (listener.success) {
          listener.success();
        }
      });
      this.audioContext.onStop(() => {
        console.log("onStop");
        if (listener.success) {
          listener.success();
        }
      });
      this.audioContext.onPlay(() => {
        console.log("play");
        if (listener.playing) {
          listener.playing();
        }
      });
    });
    this.audioContext = innerAudioContext;
  }
}

const audioPlayer = new AudioPlayer();
// export default audioPlayer;
export default audioPlayer;
