import request from "@/axios/api";
export default {
  getTopicData: (params: any) => {
    return request("/topics", "GET", params, false);
  },
  getTopicDetail: (id: string) => {
    return request(`/topics/${id}`, "GET", null, false);
  },
  getTopicHistory: (id: string) => {
    return request(`/topics/${id}/history`, "GET", null, false);
  },
  createSession: (data: any) => {
    return request(`/topics/${data.topic_id}/session`, "POST", data, true);
  },
  completeTopic: (data: any) => {
    return request(`/topics/sessions/${data.session_id}/complete`, "POST", data, true);
  },
  getTopicCompletation: (data: any) => {
    return request(`/topics/${data.topic_id}/session/${data.session_id}/completion`, "GET", null, false);
  },
  getPhrase: (data: any) => {
    return request(`/topics/${data.topic_id}/phrases`, "GET", null, false);
  },
  deleteTopicHistory: (data: any) => {
    return request(`/topics/${data.topic_id}/session/${data.session_id}`, "DELETE", null, false);
  }
};
