# <img src="https://qiniu.prejade.com/1597936949107363840/talkie/icon.png" width="60px" align="center" alt="ChatGPT-TalkieAI icon"> TalkieAI

## 简介
[TalkieAI](https://github.com/maioria/chatgpt-talkieai) 是一个基于AI的外语学习应用，可通过语音进行聊天，语法分析，翻译。
AI可以基于CHAT-GPT, 国内可以配置chat-gpt代理或者使用[智谱开放平台](https://open.bigmodel.cn/)
## 在线预览

- [TalkieAI 预览地址](https://talkie.prejade.com/)

## 微信小程序
![](https://aitake-saas-qiniu.sciotech.cn/aitake-ai/gh_8f98368aa102_258.jpg)  

## 后端
- 使用python语言开发，开发使用的版本为3.11，web框架为fastAPI，数据层框架为SQLAlchemy，语音使用azure。
## 前端
- 前端使用uniapp开发，基于vue3，可发布到网页与小程序与APP

## 项目示例图
![](https://qiniu.prejade.com/1597936949107363840/talkie/example_2.0/login.jpg)
![](https://qiniu.prejade.com/1597936949107363840/talkie/example_2.0/switch-roles.jpg)
![](https://qiniu.prejade.com/1597936949107363840/talkie/example_2.0/index.jpg)
![](https://qiniu.prejade.com/1597936949107363840/talkie/example_2.0/topic-detail.jpg)
![](https://qiniu.prejade.com/1597936949107363840/talkie/example_2.0/chat.jpg)
![](https://qiniu.prejade.com/1597936949107363840/talkie/example_2.0/chat-settings.jpg)
![](https://qiniu.prejade.com/1597936949107363840/talkie/example_2.0/chat-prompt.jpg)
![](https://qiniu.prejade.com/1597936949107363840/talkie/example_2.0/pronunciation.jpg)
![](https://qiniu.prejade.com/1597936949107363840/talkie/example_2.0/select-language.jpg)
![](https://qiniu.prejade.com/1597936949107363840/talkie/example_2.0/my.jpg)
## 本地启动
```bash
# 数据库，创建一个空的数据库，.env文件配置好数据库后启动服务，服务会自动生成相应的表，并且加载默认数据
# 1.克隆本仓库；
git clone git@github.com:maioria/chatgpt-talkieai.git
cd talkieai-server
# 2.安装依赖；
pip3 install -r requirements.txt
# 3. 启动服务（需要新建.env文件并设置变量，参考.env.default）
nohup uvicorn app.main:app --host 0.0.0.0 --port 8097 &
#前端使用HBuilder直接web或者小程序运行

# 1. 安装依赖(前端只用了俩个依赖fingerprintjs2 与 recorder)
npm install
```

## nginx配置(Web)
```bash
# uniapp可以直接跨域请求服务端地址，也可通过nginx来配置反向代理
server {
        listen       80;
        listen       [::]:80;
        server_name  {server_name};
        rewrite ^(.*) https://$server_name$1 permanent;
      }

server {
        listen       443 ssl http2;
        listen       [::]:443 ssl http2;
        server_name  {server_name};
        root         {前端编译完后的路径};
        ssl_certificate "{crt}";
        ssl_certificate_key "{key}";
        ssl_session_cache shared:SSL:1m;
        ssl_session_timeout  10m;
        ssl_ciphers HIGH:!aNULL:!MD5;
        ssl_prefer_server_ciphers on;

        # Load configuration files for the default server block.
        location ^~ /api/ {
           proxy_pass http://localhost:8000/api/;
           proxy_set_header Host $http_host;
           proxy_connect_timeout 15s;
           proxy_send_timeout 300s;
           proxy_read_timeout 300s;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }
        location / {
           try_files $uri $uri/ /index.html;
        }
    }
```
## 交流
  <div style="display:flex;">
  	<div style="padding-right:24px;">
  		<p>QQ交流群</p>
      <img src="https://qiniu.prejade.com/1597936949107363840/talkie/WechatIMG158.jpg" style="width:200px" />
  	</div>
  </div>

## 贡献
如果您有任何建议或意见，欢迎提出 [Issues](https://github.com/maioria/chatgpt-talkieai/issues) 或 [ Pull Request](https://github.com/maioria/chatgpt-talkieai/pulls)。
