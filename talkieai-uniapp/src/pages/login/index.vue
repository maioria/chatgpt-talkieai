<template>
  <view class="container">
    <image class="logo" src="/static/logo.png"></image>
    <text class="title">
      欢迎使用Talkie AI
    </text>
    <text class="sub-title">
      练习口语、写作的好帮手
    </text>
    <!-- #ifdef MP-WEIXIN -->
    <view class="mp-weixin-login-btn-box" @tap="handleWechatLogin()">
      <text class="mp-weixin-login-btn">
        小程序登录
      </text>
    </view>
    <!-- #endif -->
    <text class="visitor-login" @tap="handleVisitorLogin()">随便逛逛</text>
  </view>
</template>
  
<script setup lang="ts">
import { ref, onMounted } from 'vue';
import accountReqeust from '@/api/account';
import Fingerprint2 from 'fingerprintjs2';

const X_TOKEN = 'x-token';
const app = getApp();

const title = ref('欢迎回来！');
const second = ref(60);
const showText = ref(true);
const phone = ref('');
const password = ref('');
const yzm = ref('');
const wechatQrcodeShow = ref(false);
const wechatQrcodeUrl = ref(null);
const wechatIntervalId = ref(null);
const loginLoading = ref(false);

onMounted(() => {
  // 是否有保存登录的token
  let storageToken = uni.getStorageSync(X_TOKEN);
  if (storageToken) {
  loginSucessByToken(storageToken);
  }
});

const checkPhone = () => {
  if (!phone.value) {
    uni.showToast({
      title: '请输入手机号',
      icon: 'none'
    });
    return false;
  }
  if (!/^[1][3,4,5,7,8,9][0-9]{9}$/.test(phone.value)) {
    uni.showToast({
      title: '请输入正确手机号',
      icon: 'none'
    });
    return false;
  }
  if (!password.value) {
    uni.showToast({
      title: '请输入密码',
      icon: 'none'
    });
    return false;
  }
  return true;
};

const handlePhoneLogin = () => {
  if (loginLoading.value) {
    return;
  }
  // 检查手机号与密码不能为空
  if (!checkPhone()) {
    return;
  }
  loginLoading.value = true;
  accountReqeust.phoneLogin({
    phone: phone.value,
    password: password.value
  })
    .then((data: any) => {
      loginSuccess(data);
    })
    .finally(() => {
      loginLoading.value = false;
    });
};

const handleWechatLogin = () => {
  if (loginLoading.value) {
    return;
  }
  // 在小程序中获取登录凭证 code
  loginLoading.value = true;
  uni.login({
    success: (res) => {
      const code = res.code;
      accountReqeust.wechatLogin({
        code: code,
      })
        .then(data => {
          loginSuccess(data);
        })
        .finally(() => {
          loginLoading.value = false;
        });
    },
    fail: (err) => {
      console.error(err);
    }
  });
};

const handleVisitorLogin = () => {
  if (loginLoading.value) {
    return;
  }
  // 获取设备指纹
  loginLoading.value = true;
  Fingerprint2.get((components) => {
    const values = components.map(component => component.value);
    const fingerprint = Fingerprint2.x64hash128(values.join(''), 31);

    // 在这里可以将设备指纹发送到服务器进行处理
    console.log('设备指纹:', fingerprint);

    accountReqeust.visitorLogin({
      fingerprint: fingerprint
    })
      .then(data => {
        loginSuccess(data)
      })
      .finally(() => {
        loginLoading.value = false;
      });
  });
};

/**
 * 用户登录请求结果处理
 */
const loginSuccess = (data: any) => {
  if (data.code !== '200') {
    uni.showToast({
      title: data.message,
      icon: 'none'
    });
    return;
  }
  let storageToken = data.data;
  loginSucessByToken(storageToken);
};

/**
 * 通过用户token加载后续逻辑
 */
const loginSucessByToken = (storageToken: string) => {
  uni.setStorageSync('x-token', storageToken);
  uni.switchTab({
    url: '/pages/index/index'
  });
};

</script>
<style scoped lang="less">
.container {
  padding: 380rpx 48rpx 0 48rpx;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;

  .logo {
    width: 120rpx;
    height: 120rpx;
  }

  .title {
    margin-top: 60rpx;
    width: 430rpx;
    height: 67rpx;
    font-size: 48rpx;
    font-weight: 600;
    color: #000000;
    line-height: 67rpx;
    letter-spacing: 1px;
  }

  .sub-title {
    margin-top: 20rpx;
    margin-bottom: 160rpx;
    width: 390rpx;
    height: 45rpx;
    font-size: 32rpx;
    color: #939193;
    line-height: 45rpx;
    letter-spacing: 1px;
  }

  .mp-weixin-login-btn-box {
    width: 100%;
    height: 90rpx;
    border-radius: 60rpx;
    background-color: #5456EB;
    display: flex;
    align-items: center;
    justify-content: center;

    .mp-weixin-login-btn {
      color: #fff;
      font-size: 32rpx;
      font-weight: 400;
      height: 45rpx;
      line-height: 45rpx;
    }
  }

  .visitor-login {
    margin-top: 40rpx;
    height: 45rpx;
    font-size: 32rpx;
    font-weight: 400;
    color: #6236FF;
    line-height: 45rpx;
    letter-spacing: 1px;
  }
}
</style>