import request from "@/axios/api";
export default {
  sessionCreate: (data: any) => {
    return request("/sessions", "POST", data, true);
  },
  sessionDefaultGet: (data: any) => {
    return request("/sessions/default", "GET", data, true);
  },
  sessionDetailsGet: (data: any) => {
    return request("/sessions/" + data.sessionId, "GET", data, true);
  },
  sessionInitGreeting: (sessionId:string) => {
    return request("/sessions/" + sessionId + "/greeting", "GET", {}, false);
  },
  sessionChatInvoke: (data: any) => {
    return request("/" + data.sessionId + "/chat", "POST", data, false);
  },
  speechContent: (data: any) => {
    return request("/speech-content", "POST", data, false);
  },
  speechDemo: (data: any) => {
    return request("/speech-demo", "POST", data, false);
  },
  grammarInvoke: (data: any) => {
    return request("/grammar", "POST", data, false);
  },
  pronunciationInvoke: (data: any) => {
    return request("/pronunciation", "POST", data, false);
  },
  translateInvoke: (data: any) => {
    return request("/translate", "POST", data, false);
  },
  transformText: (data: any) => {
    return request(
      `/sessions/${data.sessionId}/voice-translate`,
      "POST",
      data,
      false
    );
  },
  translateText: (data: any) => {
    return request("/translate-text", "POST", data, false);
  },
  transferSpeech: (data: any) => {
    return request("/speech", "POST", data, false);
  },
  wordDetail: (data: any) => {
    return request("/word/detail", "POST", data, false);
  },
  wordPractice: (data: any) => {
    return request("/word/practice", "POST", data, false);
  },
  messagePractice: (data: any) => {
    return request(`/message/${data.message_id}/practice`, "POST", data, false);
  },
  promptInvoke: (data: any) => {
    return request("/prompt", "POST", data, false);
  },
  messagesAllDelete: (sessionId: string) => {
    return request(`/sessions/${sessionId}/messages`, "DELETE", null, false);
  }
};
