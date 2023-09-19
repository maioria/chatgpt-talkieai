<template>
  <Speech @success="handleSuccess" ref="speechRef">
      <template v-slot:leftMenu>
          <slot name="leftMenu">
          </slot>
      </template>
      <template v-slot:rightMenu>
          <slot name="rightMenu">
          </slot>
      </template>
  </Speech>
</template>
<script setup lang="ts">
import { getCurrentInstance, defineEmits } from "vue";
import Speech from "@/components/Speech.vue";

const emit = defineEmits();
const $bus: any = getCurrentInstance()?.appContext.config.globalProperties.$bus;

/**
* {fileName}
*/
const handleSuccess = (data: any) => {
  const fileName = data.fileName;
  emit("success", data);
  $bus.emit("SendMessage", {
      fileName: fileName
  });
};
</script>