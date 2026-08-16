<template>
  <div class="profile-page">
    <van-nav-bar
      title="个人信息"
      left-arrow
      @click-left="$router.back()"
      fixed
    />
    
    <div class="profile-container">
      <van-cell-group inset class="avatar-group">
        <van-cell title="头像" center is-link @click="showAvatarDialog">
          <template #right-icon>
            <van-image
              round
              width="60"
              height="60"
              :src="userAvatar"
            />
          </template>
        </van-cell>
      </van-cell-group>
      
      <van-cell-group inset class="info-group">
        <van-cell title="用户名" :value="userInfo.username || ''" />
        <van-cell title="账号ID" :value="`ID: ${userId}`" />
        <van-cell title="昵称" :value="userNickname" is-link @click="showNicknameDialog" />
        <van-cell title="性别" :value="userGenderText" is-link @click="showGenderPopup = true" />
        <van-cell title="手机号" :value="userPhone || '未绑定'" is-link @click="showPhoneDialog" />
        <van-cell title="个人简介" :value="userBio" is-link @click="showBioDialog" />
      </van-cell-group>
      
      <van-cell-group inset class="security-group">
        <van-cell title="修改密码" is-link @click="showPasswordConfirm" />
      </van-cell-group>
    </div>

    <!-- 性别选择弹出层 -->
    <van-popup v-model:show="showGenderPopup" position="bottom" round>
      <div class="popup-title">选择性别</div>
      <van-cell-group inset>
        <van-cell
          v-for="gender in genderOptions"
          :key="gender.value"
          :title="gender.label"
          clickable
          :class="{ 'gender-active': currentGender === gender.value }"
          @click="selectGender(gender.value)"
        >
          <template #right-icon>
            <van-radio :name="gender.value" />
          </template>
        </van-cell>
      </van-cell-group>
    </van-popup>
  </div>
</template>

<script setup>
import { ref, computed, h, onMounted } from 'vue';
import { useUserStore } from '../store/user';
import { showDialog, showToast, showLoadingToast, showSuccessToast, showFailToast } from 'vant';
import { useRouter } from 'vue-router';

const router = useRouter();
const userStore = useUserStore();

// 初始化用户状态
onMounted(async () => {
  // 如果用户未登录，跳转到登录页面
  if (!userStore.getLoginStatus) {
    router.push('/login');
    return;
  }
  
  // 获取用户信息
  try {
    // 显示加载提示
    const loadingInstance = showLoadingToast({
      message: '加载中...',
      forbidClick: true,
      duration: 0
    });
    
    const result = await userStore.getUserInfoDetail();
    
    // 手动关闭加载提示
    loadingInstance.close();
    
    if (result.success) {
      console.log('获取用户信息成功:', userStore.userInfo);
    } else {
      console.error('获取用户信息失败:', result.message);
      showFailToast(result.message || '获取用户信息失败');
    }
  } catch (error) {
    console.error('获取用户信息请求失败:', error);
    showToast.clear();
    showToast.fail('获取用户信息失败');
  }
});

const userInfo = computed(() => userStore.userInfo);
const userId = computed(() => userInfo.value?.id || 'N/A');
const userAvatar = computed(() => userInfo.value?.avatar || 'https://fastly.jsdelivr.net/npm/@vant/assets/cat.jpeg');
const userNickname = computed(() => userInfo.value?.nickname || '未设置');
const userPhone = computed(() => userInfo.value?.phone || '');
const userBio = computed(() => userInfo.value?.bio || '暂无简介');

// 性别展示与选项
const genderOptions = [
  { label: '男', value: 'male' },
  { label: '女', value: 'female' },
  { label: '保密', value: 'unknown' }
];
const currentGender = computed(() => userInfo.value?.gender || 'unknown');
const userGenderText = computed(() => {
  const match = genderOptions.find(item => item.value === currentGender.value);
  return match ? match.label : '保密';
});
const showGenderPopup = ref(false);

// 通用保存方法：调用后端更新接口并刷新本地用户信息
const saveUserInfo = async (data, successMsg, failMsg) => {
  try {
    const loadingInstance = showLoadingToast({
      message: '保存中...',
      forbidClick: true,
      duration: 0
    });
    
    const result = await userStore.updateUserInfo(data);
    
    loadingInstance.close();
    
    if (result && result.success) {
      showSuccessToast(successMsg);
    } else {
      showFailToast((result && result.message) || failMsg);
    }
  } catch (error) {
    console.error('更新用户信息失败:', error);
    showToast.clear();
    showToast.fail(failMsg);
  }
};

// 修改头像（项目暂无文件上传接口，支持输入图片URL）
const showAvatarDialog = () => {
  const newValue = ref(userAvatar.value);
  
  showDialog({
    title: '修改头像',
    showCancelButton: true,
    confirmButtonText: '确认',
    className: 'profile-dialog',
    message: h('div', { style: 'text-align: left; padding: 10px 0;' }, [
      h('div', { style: 'margin-bottom: 5px; text-align: left;' }, '头像URL：'),
      h('input', {
        type: 'text',
        value: newValue.value,
        onInput: (e) => { newValue.value = e.target.value },
        style: 'width: 100%; border: 1px solid #dcdee0; border-radius: 4px; padding: 8px; box-sizing: border-box;'
      })
    ])
  }).then(async () => {
    const val = newValue.value.trim();
    if (!val) {
      showToast('头像URL不能为空');
      return;
    }
    if (val === (userInfo.value?.avatar || '')) {
      return;
    }
    await saveUserInfo({ avatar: val }, '头像修改成功', '头像修改失败');
  }).catch(() => {
    // 点击取消
  });
};

// 修改昵称
const showNicknameDialog = () => {
  const newValue = ref(userNickname.value);
  
  showDialog({
    title: '修改昵称',
    showCancelButton: true,
    confirmButtonText: '确认',
    className: 'profile-dialog',
    message: h('div', { style: 'text-align: left; padding: 10px 0;' }, [
      h('div', { style: 'margin-bottom: 5px; text-align: left;' }, '昵称：'),
      h('input', {
        type: 'text',
        maxlength: 50,
        value: newValue.value,
        onInput: (e) => { newValue.value = e.target.value },
        style: 'width: 100%; border: 1px solid #dcdee0; border-radius: 4px; padding: 8px; box-sizing: border-box;'
      })
    ])
  }).then(async () => {
    const val = newValue.value.trim();
    if (!val) {
      showToast('昵称不能为空');
      return;
    }
    if (val === (userInfo.value?.nickname || '')) {
      return;
    }
    await saveUserInfo({ nickname: val }, '昵称修改成功', '昵称修改失败');
  }).catch(() => {
    // 点击取消
  });
};

// 修改手机号
const showPhoneDialog = () => {
  const newValue = ref(userPhone.value);
  
  showDialog({
    title: '修改手机号',
    showCancelButton: true,
    confirmButtonText: '确认',
    className: 'profile-dialog',
    message: h('div', { style: 'text-align: left; padding: 10px 0;' }, [
      h('div', { style: 'margin-bottom: 5px; text-align: left;' }, '手机号：'),
      h('input', {
        type: 'tel',
        maxlength: 12,
        value: newValue.value,
        onInput: (e) => { newValue.value = e.target.value },
        style: 'width: 100%; border: 1px solid #dcdee0; border-radius: 4px; padding: 8px; box-sizing: border-box;'
      })
    ])
  }).then(async () => {
    const val = newValue.value.trim();
    if (!val) {
      showToast('手机号不能为空');
      return;
    }
    if (val === (userInfo.value?.phone || '')) {
      return;
    }
    await saveUserInfo({ phone: val }, '手机号修改成功', '手机号修改失败');
  }).catch(() => {
    // 点击取消
  });
};

// 选择性别
const selectGender = (value) => {
  showGenderPopup.value = false;
  if (value === (userInfo.value?.gender || 'unknown')) {
    return;
  }
  saveUserInfo({ gender: value }, '性别修改成功', '性别修改失败');
};

// 修改个人简介
const showBioDialog = () => {
  const newBioValue = ref(userBio.value);
  
  showDialog({
    title: '修改个人简介',
    showCancelButton: true,
    confirmButtonText: '确认',
    className: 'bio-dialog',
    message: h('div', { style: 'text-align: left; padding: 10px 0;' }, [
      h('div', { style: 'margin-bottom: 15px;' }, [
        h('div', { style: 'margin-bottom: 5px; text-align: left;' }, '个人简介：'),
        h('textarea', {
          value: newBioValue.value,
          onInput: (e) => { newBioValue.value = e.target.value },
          style: 'width: 100%; border: 1px solid #dcdee0; border-radius: 4px; padding: 8px; box-sizing: border-box; min-height: 100px; resize: vertical;'
        })
      ])
    ])
  }).then(async () => {
    // 无修改，直接return，不会出现loading、不会调用接口
    if (userBio.value.trim() === newBioValue.value.trim()) {
      return;
    }
    await saveUserInfo({ bio: newBioValue.value.trim() }, '个人简介修改成功', '个人简介修改失败');
  }).catch(() => {
    // 点击取消
  });
};

// 修改密码
const showPasswordConfirm = () => {
  const oldPassword = ref('');
  const newPassword = ref('');
  const confirmPassword = ref('');
  
  showDialog({
    title: '修改密码',
    showCancelButton: true,
    className: 'password-dialog',
    message: h('div', { style: 'text-align: left; padding: 10px 0;' }, [
      h('div', { style: 'margin-bottom: 15px;' }, [
        h('div', { style: 'margin-bottom: 5px; text-align: left;' }, '当前密码：'),
        h('input', {
          type: 'password',
          value: oldPassword.value,
          onInput: (e) => { oldPassword.value = e.target.value },
          style: 'width: 100%; border: 1px solid #dcdee0; border-radius: 4px; padding: 8px; box-sizing: border-box;'
        })
      ]),
      h('div', { style: 'margin-bottom: 15px;' }, [
        h('div', { style: 'margin-bottom: 5px; text-align: left;' }, '新密码：'),
        h('input', {
          type: 'password',
          value: newPassword.value,
          onInput: (e) => { newPassword.value = e.target.value },
          style: 'width: 100%; border: 1px solid #dcdee0; border-radius: 4px; padding: 8px; box-sizing: border-box;'
        })
      ]),
      h('div', { style: 'margin-bottom: 15px;' }, [
        h('div', { style: 'margin-bottom: 5px; text-align: left;' }, '确认密码：'),
        h('input', {
          type: 'password',
          value: confirmPassword.value,
          onInput: (e) => { confirmPassword.value = e.target.value },
          style: 'width: 100%; border: 1px solid #dcdee0; border-radius: 4px; padding: 8px; box-sizing: border-box;'
        })
      ])
    ]),
  }).then(async () => {
    if (!oldPassword.value) {
      showToast('请输入当前密码');
      return;
    }
    
    if (!newPassword.value) {
      showToast('请输入新密码');
      return;
    }
    
    if (newPassword.value !== confirmPassword.value) {
      showToast('两次密码输入不一致');
      return;
    }
    
    try {
      const loadingInstance = showLoadingToast({
        message: '修改中...',
        forbidClick: true,
        duration: 0
      });
      
      const result = await userStore.updatePassword(oldPassword.value, newPassword.value);
      
      loadingInstance.close();
      
      if (result && result.success) {
        showSuccessToast('密码修改成功');
      } else {
        showFailToast((result && result.message) || '密码修改失败');
      }
    } catch (error) {
      console.error('修改密码失败:', error);
      showToast.clear();
      showToast.fail('密码修改失败');
    }
  }).catch(() => {
    // 点击取消按钮
  });
};
</script>

<style scoped>
.profile-page {
  min-height: 100vh;
  background-color: #f7f8fa;
}

.profile-container {
  padding-top: 56px;
  padding-bottom: 20px;
}

.avatar-group,
.info-group,
.security-group {
  margin-top: 12px;
}

.popup-title {
  text-align: center;
  padding: 16px;
  font-size: 16px;
  font-weight: bold;
  border-bottom: 1px solid #eee;
}

.gender-active {
  background-color: #f5f5f5;
}
</style>
