import request from "@/axios/api";
export default {
  wechatLogin: (data: any) => {
    return request("/wechat/code-login", "POST", data, true);
  },
  visitorLogin: (data: any) => {
    return request("/visitor-login", "POST", data, true);
  },
	phoneLogin: (data: any) => {
		return request('/phone-login', 'POST', data, true);
	},
  accountInfoGet: () => {
    return request("/account-info", "GET");
  },
  settingsPost: (data: any) => {
    return request("/settings", "POST", data);
  },
  settingsGet: () => {
    return request("/settings", "GET");
  },
};
