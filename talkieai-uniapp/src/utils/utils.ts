export default {
  isWechat: () => {
    const ua = navigator.userAgent.toLowerCase();
    return ua.indexOf("micromessenger") !== -1;
  },
  removeDecimal: (num: number) => {
    return Math.floor(num);
  },
};
