<template>
    <view>
        切换角色
    </view>
</template>
<script setup lang="ts">
import { ref, onMounted, watch } from "vue";
import type { Language, Role } from './model'
import roleRequest from './service';

const languages = ref<Language[]>([]);
const roles = ref<Role[]>([]);
const selectedLanguage = ref<Language>();

onMounted(() => {
    roleRequest.languagesGet().then(data => {
        languages.value = data.data;
        selectedLanguage.value = data.data[0];
        initRoles();
    });
    uni.setNavigationBarTitle({
        title: 'TalkieAI'
    });
})
const initRoles = () => {
    if (!selectedLanguage.value) {
        return;
    }
    roleRequest.rolesGet({ language: selectedLanguage.value.id }).then(data => {
        roles.value = data.data;
    })
}
</script>
<style scoped lang="less"></style>