import request from "@/axios/api";
export default {
  languagesGet: (data?: any) => {
    return request("/languages", "GET", data, false);
  },
  rolesGet: (data?: any) => {
    return request("/roles", "GET", data, false);
  },
};
