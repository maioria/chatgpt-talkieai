export default {
	methods: {
		// 获取聊天教师的头像
		getTeacherAvatar(avatar, gender, feel) {
			if (avatar) {
				return avatar;
			}
			if (gender === 'FEMALE') {
				return '/static/img/teacher-female-avatar.jpg'
			} else {
				return '/static/img/teacher-male-avatar.jpg'
			}
		},
		// 判断当前语种是不是汉语
		isChinese(session) {
			if (!session) {
				return false;
			}
			return session.language.startsWith('zh-')
		}
	}
}