import __config from "@/config/env";

const request = (
  url: string,
  method?:
    | "OPTIONS"
    | "GET"
    | "HEAD"
    | "POST"
    | "PUT"
    | "DELETE"
    | "TRACE"
    | "CONNECT",
  data?: any,
  showLoading?: boolean
): Promise<any> => {
  let _url = __config.basePath + url;
  return new Promise((resolve, reject) => {
    if (showLoading) {
      uni.showLoading();
    }
    uni.request({
      url: _url,
      method: method,
      data: data,
      header: {
        "Content-Type": "application/json",
        "X-Token": uni.getStorageSync("x-token")
          ? uni.getStorageSync("x-token")
          : "",
      },
      success(res) {
        if (res.statusCode == 200) {
          resolve(res.data);
        } else if (res.statusCode == 401) {
          uni.showToast({
            title: "登录过期，重新登录",
            icon: "none",
            duration: 2000,
          });
          uni.removeStorageSync("x-token");
          uni.navigateTo({
            url: "/pages/login/index",
          });
        } else {
          reject(res.data);
        }
      },
      fail(error) {
        console.error(error);
        reject(error);
      },
      complete(res) {
        // 判断是否在loading中
        if (showLoading) {
          uni?.hideLoading();
        }
      },
    });
  });
};
export default request;
