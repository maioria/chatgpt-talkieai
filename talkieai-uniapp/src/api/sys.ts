import request from "@/axios/api";
export default {
  feedbackAdd: (data: any) => {
    return request("/sys/feedback", "POST", data, false);
  },
  getLanguages: () => {
    return request("/sys/languages", "GET", null);
  },
  getRoles: (data: any) => {
    return request("/sys/roles", "GET", data);
  },
  setLearningLanguage: (data: any) => {
    return request("/sys/language", "POST", data);
  },
  settingsPost: (data: any) => {
    return request("/sys/settings", "POST", data);
  },
  settingsGet: () => {
    return request("/sys/settings", "GET");
  },
};
