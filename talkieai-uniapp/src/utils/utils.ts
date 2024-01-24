import __config from "@/config/env";

export default {
  isWechat: () => {
    const ua = navigator.userAgent.toLowerCase();
    return ua.indexOf("micromessenger") !== -1;
  },
  removeDecimal: (num: number) => {
    return Math.floor(num);
  },
  getVoiceFileUrl: (fileName: string) => {
    return `${__config.basePath}/voices/${fileName}`;
  },
};
