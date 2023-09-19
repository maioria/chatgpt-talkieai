import { ref, onMounted } from "vue";
import chatRequest from "@/api/chat";
// 全局状态，创建在模块作用域下
const globalUserInfo = ref(1);
const globalLoading = ref(false);

export function useUserInfo() {
  // 局部状态，每个组件都会创建
  const localCount = ref(1);
  onMounted(() => {
    globalLoading.value = true;
    chatRequest.sessionDefaultGet({}).then((data) => {
      globalUserInfo.value = data.data;
    });
    globalLoading.value = false;
  });
  return {
    globalUserInfo,
    globalLoading,
    localCount,
  };
}
