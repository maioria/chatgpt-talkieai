import request from "@/axios/api";
export default {
  visitorLogin: (data: any) => {
    return request("/account/visitor-login", "POST", data, true);
  },
  accountInfoGet: () => {
    return request("/account/info", "GET");
  },
  setSettings: (data: any) => {
    return request("/account/settings", "POST", data);
  },
  getSettings: () => {
    return request("/account/settings", "GET");
  },
  setRole: (data: any) => {
    return request("/account/role", "POST", data);
  },
  getRole: () => {
    return request("/account/role", "GET", null);
  },
  setLearningLanguage: (data: any) => {
    return request("/account/language", "POST", data);
  },
  getLearningLanguage: () => {
    return request("/account/language", "GET", null);
  },
  collectGet: (data: any) => {
    return request("/account/collect", "GET", data, false);
  },
  collect: (data: any) => {
    return request("/account/collect", "POST", data, false);
  },
  cancelCollect: (data: any) => {
    return request("/account/collect", "DELETE", data, false);
  },
  collectsGet: (data: any) => {
    return request("/account/collects", "GET", data, false);
  }
};
