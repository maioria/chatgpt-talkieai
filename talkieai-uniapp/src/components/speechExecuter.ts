import __config from "@/config/env";

// #ifdef H5
import Recorder from "recorder-core";
import "recorder-core/src/engine/wav";
// #endif

/**
 * 录音后自动上传文件，成功后回调文件名
 */

const MAXIMUM_RECORDING_TIME = 60;

class Speech {
  private recorder = {
    start: false,
    processing: false,
    remainingTime: 0,
    rec: null as any | null,
    wxRecorderManager: null,
  };
  private intervalId: any = null;
  private listener = {
    success: null as Function | null,
    cancel: null as Function | null,
    error: null as Function | null,
    interval: null as Function | null,
    processing: null as Function | null,
  };

  constructor() {
    // ... Constructor logic ...
  }

  handleVoiceStart({
    success,
    cancel,
    error,
    interval,
    processing,
  }: {
    success: Function;
    cancel: Function;
    error: Function;
    interval: Function;
    processing: Function;
  }) {
    let self = this;
    self.listener.success = success;
    self.listener.cancel = cancel;
    self.listener.error = error;
    self.listener.interval = interval;
    self.listener.processing = processing;

    // #ifndef H5
    self.mpWeixinVoiceStart();
    // #endif

    // #ifdef H5
    self.h5VoiceStart();
    // #endif
  }

  mpWeixinVoiceStart() {
    let self = this;
    let recorderManager = uni.getRecorderManager();
	console.log(recorderManager)
    // 如果是andoird手机使用，则须要设置mp3格式，否则无法播放
    let format = "wav";
    if (uni.getSystemInfoSync().platform === "android") {
      format = "mp3";
    }
    self.recorder.wxRecorderManager = recorderManager;
    recorderManager.start({
      duration: MAXIMUM_RECORDING_TIME * 1000,
      sampleRate: 44100,
      encodeBitRate: 192000,
      format: format,
    });
	console.log('speech start..')
    self.recorder.start = true;
    self.recorder.remainingTime = MAXIMUM_RECORDING_TIME;
    self.intervalId = setInterval(() => {
      if (self.recorder.remainingTime === 0) {
        self.handleEndVoice();
      } else {
        if (self.listener.interval) {
          self.listener.interval(self.recorder.remainingTime);
        }
        self.recorder.remainingTime--;
      }
    }, 1000);

    recorderManager.onStop((res: any) => {
		console.log('speech on stop..' + res.tempFilePath);
      self.handleProcessWxEndVoice({
        filePath: res.tempFilePath,
      });
    });
  }

  clearInterval() {
    const self = this;
    if (self.intervalId) {
      clearInterval(self.intervalId);
    }
  }

  h5VoiceStart() {
    let self = this;
    self.recorder.rec = Recorder({
      type: "wav",
      bitRate: 32,
      sampleRate: 32000,
    });
    self.recorder.rec.open(
      () => {
        self.recorder.start = true;
        self.recorder.rec.start();
        self.recorder.remainingTime = MAXIMUM_RECORDING_TIME;
        self.intervalId = setInterval(() => {
          if (self.listener.interval) {
            self.listener.interval(self.recorder.remainingTime);
          }
          if (self.recorder.remainingTime === 0) {
            clearInterval(self.intervalId);
            self.handleEndVoice();
          } else {
            self.recorder.remainingTime--;
          }
        }, 1000);
      },
      (msg: string, isUserNotAllow: any) => {
        uni.showToast({
          title: "请开启录音权限",
          icon: "none",
        });
        if (self.listener.error) {
          self.listener.error(msg);
        }
      }
    );
  }

  handleCancleVoice() {
    let self = this;
    self.clearInterval();

    // #ifndef H5
    if (self.recorder.wxRecorderManager) {
      self.recorder.wxRecorderManager.stop();
      self.recorder.start = false;
      self.recorder.processing = false;
      self.recorder.wxRecorderManager = null;
    }
    // #endif

    // #ifdef H5
    if (self.recorder.rec) {
      self.recorder.rec.stop(() => {
        self.recorder.start = false;
        self.recorder.processing = false;
        self.recorder.rec = null;
      });
    }
    // #endif

    if (self.listener.cancel) {
      self.listener.cancel();
    }
  }

  handleEndVoice() {
    let self = this;
    self.clearInterval();

    if (self.recorder.processing) {
      return;
    }

    // #ifndef H5
	console.log('speech trigger end..')
    self.handleWxEndVoice();
    // #endif

    // #ifdef H5
    self.handleH5EndVoice();
    // #endif
  }

  handleWxEndVoice() {
    let self = this;
	console.log('execute stop1')
	console.log(self.recorder)
    self.recorder.wxRecorderManager.stop();
	console.log('execute stop')
  }

  handleProcessWxEndVoice({ filePath }: { filePath: string }) {
	  console.log('speech end...')
    let self = this;
    if (self.listener.processing) {
      self.listener.processing();
    }

    uni.uploadFile({
      url: __config.basePath + "/voice/upload",
      filePath: filePath,
      header: {
        "X-Token": uni.getStorageSync("x-token"),
      },
      name: "file",
      success: (res:any) => {
        var resData = res;
        self.handleUploadResult({
          resData,
        });
      },
      fail(e:any) {
        console.error(e, "失败原因");
        uni.showToast({
          title: "上传失败",
          icon: "none",
        });
        if (self.listener.error) {
          self.listener.error(e);
        }
      },
      complete: () => {
        self.recorder.start = false;
        self.recorder.processing = false;
        self.recorder.rec = null;
      },
    });
  }

  handleH5EndVoice() {
    let self = this;
    if (self.listener.processing) {
      self.listener.processing();
    }

    self.recorder.rec.stop(
      (blob:any, duration:any) => {
        self.recorder.processing = true;
        var reader = new FileReader();
        reader.addEventListener("load", function () {}, false);
        reader.readAsDataURL(blob);
        let blobURL = window.URL.createObjectURL(blob);

        uni.uploadFile({
          file: blob,
          header: {
            "X-Token": uni.getStorageSync("x-token"),
          },
          name: "file",
          formData: {
            file: blob,
          },
          url:
            __config.basePath + "/voice/upload",
          success: (res) => {
            var resData = res;
            self.handleUploadResult({
              resData,
            });
          },
          fail(e) {
            console.error(e, "失败原因");
            uni.showToast({
              title: "上传失败",
              icon: "none",
            });
          },
          complete: () => {
            self.recorder.start = false;
            self.recorder.processing = false;
            self.recorder.rec = null;
          },
        });
      },
      function (s:any) {
        if (self.listener.error) {
          self.listener.error(s);
        }
        console.error("结束出错");
      },
      true
    );
  }

  handleUploadResult({ resData }: { resData: any }) {
    const self = this;
    if (resData.statusCode == 200) {
      let resultJson = JSON.parse(resData.data);
      if (resultJson.code != "200") {
        uni.showToast({
          title: resultJson.message,
          icon: "none",
        });
        if (self.listener.error) {
          self.listener.error(resultJson);
        }
        return;
      }
      let dataJson = resultJson.data;
      if (self.listener.success) {
        self.listener.success({
          inputValue: dataJson.result,
          voiceFileName: dataJson.file,
        });
      }
    }
  }
}

const speech = new Speech();
export default speech;
