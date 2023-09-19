<template>
  <view class="checkbox-box" @tap="checkIt">
    <image :class="isCheck ? 'checkbox-box-ico' : 'checkbox-box-ico un-checkbox-box-ico'
      " src="../static/check.png" />
    <image :class="!isCheck ? 'checkbox-box-ico' : 'checkbox-box-ico un-checkbox-box-ico'
      " src="../static/un_check.png" />
  </view>
</template>

<script setup lang="ts">
import { ref, watch, defineEmits, onMounted } from "vue";
interface Props {
  [date: string]: any;
  checked?: boolean;
}

const props = defineProps<Props>();
const title = ref("Hello");
const isCheck = ref(false);
setTimeout(() => {
  title.value = "首页";
}, 3000);

const emit = defineEmits<{
  (event: "input", value: boolean): void;
}>();

const checkIt = (e: any) => {
  e.stopPropagation();
  isCheck.value = !isCheck.value;
  emit("input", isCheck.value);
};

watch(
  () => props.checked,
  (newVal) => {
    console.log("props.checked", props.checked);
    isCheck.value = !!props.checked;
  }
);

onMounted(() => {
  console.log("props.checked", props.checked);
  isCheck.value = !!props.checked;
});
</script>

<style lang="less">
.checkbox-box {
  width: 76rpx;
  height: 40rpx;
  position: relative;

  .checkbox-box-ico {
    width: 76rpx;
    height: 40rpx;
    position: absolute;
    top: 0;
    left: 0;
    transition: all 0.5 linear;
  }

  .un-checkbox-box-ico {
    width: 0;
    opacity: 0;
  }
}
</style>
