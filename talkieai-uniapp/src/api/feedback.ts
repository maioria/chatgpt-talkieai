import request from "@/axios/api";
export default {
  feedbackAdd: (data: any) => {
    return request("/feedback", "POST", data, false);
  },
};