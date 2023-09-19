import request from "@/axios/api";
export default {
  wechatLogin: (data: any) => {
		return request('/wechat/code-login', "POST", data, false);
	},
	visitorLogin: (data: any) => {
		return request('/visitor-login', "POST", data, false);
	}
};
