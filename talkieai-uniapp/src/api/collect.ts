import request from "@/axios/api";
export default {
  collectGet: (data: any) => {
    return request("/collect", "GET", data, false);
  },
  collect: (data: any) => {
    return request("/collect", "POST", data, false);
  },
  cancelCollect: (data: any) => {
    return request("/collect", "DELETE", data, false);
  },
  collectsGet: (data: any) => {
    return request("/collects", "GET", data, false);
  }
};
