// import axios from "axios";
// import Cookies from "js-cookie";
// axios.interceptors.request.use(
//   function (config) {
//     // 在发送请求之前做些什么
//     let configCp = { ...config };
//     const token = Cookies.get("token");
//     const authHeader = {
//       Authorization: `${token}`,
//       headers: {
//         "Content-Type": "application/json",
//       },
//     };
//     configCp.headers = {
//       ...configCp.headers,
//       ...authHeader,
//     } as any;
//     return configCp;
//   },
//   function (error) {
//     // 对请求错误做些什么
//     return Promise.reject(error);
//   }
// );

// // 添加响应拦截器
// axios.interceptors.response.use(
//   function (response) {
//     // 2xx 范围内的状态码都会触发该函数。
//     // 对响应数据做点什么
//     console.log("response", response);
//     if (response.status == 200) {
//       if (response.data.code === 401) {
//         Cookies.remove("token");
//         window.location.href = "./login";
//         // Toast.show(response.data.message || "Server Internal Error");
//       } else if (response.data.code !== 200) {
//         // Toast.show(response.data.message || "Server Internal Error");
//       }
//     } else if (response.status == 200) {
//       // Toast.show("Server Internal Error");
//     } else if (response.status != 200) {
//       // Toast.show("Server Internal Error");
//     }
//     return response;
//   },
//   function (response) {
//     // 超出 2xx 范围的状态码都会触发该函数。
//     // 对响应错误做点什么
//     if (response.status == 200 && response.data.code !== 200) {
//       // Toast.show(response.data.message || "Server Internal Error");
//     } else if (response.status != 200) {
//       // Toast.show("Server Internal Error");
//     }
//     return response;
//   }
// );

// export default axios;
